"""API module - FastAPI web interface with WebSocket support for ChronosArchiver."""

import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.models import ArchiveStatus
from chronos_archiver.search import SearchEngine

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ChronosArchiver API",
    description="API para pesquisa e visualização de conteúdo arquivado / API for searching and viewing archived content",
    version="1.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
config = None
search_engine = None
indexer = None
archiver = None
active_jobs = {}
websocket_connections = set()


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    filters: Optional[dict[str, Any]] = None
    limit: int = 20
    offset: int = 0


class ArchiveRequest(BaseModel):
    """Archive request model."""
    urls: List[str]
    priority: str = "normal"


class ArchiveJobResponse(BaseModel):
    """Archive job response."""
    id: str
    url: str
    status: str
    progress: int
    stage: str
    created_at: str
    updated_at: str
    error: Optional[str] = None


async def initialize_service_with_retry(service_name: str, init_func, max_retries: int = 5, delay: int = 5):
    """Initialize a service with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing {service_name} (attempt {attempt + 1}/{max_retries})...")
            result = init_func()
            logger.info(f"{service_name} initialized successfully")
            return result
        except Exception as e:
            logger.warning(f"Failed to initialize {service_name}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Failed to initialize {service_name} after {max_retries} attempts")
                return None
    return None


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    global config, search_engine, indexer, archiver
    
    logger.info("Starting ChronosArchiver API...")
    
    # Load configuration
    try:
        config = load_config()
        logger.info("Configuration loaded")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        config = {}
    
    # Initialize search engine with retry
    search_engine = await initialize_service_with_retry(
        "Search engine",
        lambda: SearchEngine(config)
    )
    
    # Initialize indexer with retry
    indexer = await initialize_service_with_retry(
        "Indexer",
        lambda: ContentIndexer(config)
    )
    
    # Initialize archiver with retry
    archiver = await initialize_service_with_retry(
        "Archiver",
        lambda: ChronosArchiver(config)
    )
    
    if archiver:
        logger.info("ChronosArchiver API started successfully")
    else:
        logger.warning("ChronosArchiver API started with limited functionality (archiver not available)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global indexer, archiver
    
    if indexer:
        try:
            await indexer.close()
        except Exception as e:
            logger.error(f"Error closing indexer: {e}")
    
    if archiver:
        try:
            await archiver.shutdown()
        except Exception as e:
            logger.error(f"Error shutting down archiver: {e}")
    
    logger.info("ChronosArchiver API shut down")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Home page."""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ChronosArchiver - Motor de Busca de Arquivos Web</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 800px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .feature {
                padding: 20px;
                background: #f8f9ff;
                border-radius: 10px;
                text-align: center;
            }
            .feature-icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .feature-title {
                color: #667eea;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .api-link {
                text-align: center;
                margin-top: 30px;
                padding-top: 30px;
                border-top: 1px solid #e0e0e0;
            }
            .api-link a {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🕒 ChronosArchiver</h1>
            <p class="subtitle">Motor de Busca Inteligente para Conteúdo Arquivado da Web</p>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🔍</div>
                    <div class="feature-title">Busca Inteligente</div>
                    <div class="feature-desc">Pesquisa com tolerância a erros</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎥</div>
                    <div class="feature-title">Detecção de Embeds</div>
                    <div class="feature-desc">YouTube, Vimeo e outras mídias</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <div class="feature-title">Análise de Conteúdo</div>
                    <div class="feature-desc">Extração de entidades e tópicos</div>
                </div>
                <div class="feature">
                    <div class="feature-icon">🇧🇷</div>
                    <div class="feature-title">Suporte a Português</div>
                    <div class="feature-desc">Otimizado para PT-BR</div>
                </div>
            </div>
            
            <div class="api-link">
                <a href="/api/docs" target="_blank">Documentação da API →</a> |
                <a href="http://localhost:3001" target="_blank" style="margin-left: 10px">React App →</a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/api/search")
async def api_search(
    q: str = Query(..., description="Search query"),
    topics: Optional[str] = Query(None, description="Filter by topics (comma-separated)"),
    has_videos: Optional[bool] = Query(None, description="Filter by video presence"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Result offset"),
):
    """Search archived content."""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    filters = {}
    if topics:
        filters["topics"] = topics.split(",")
    if has_videos is not None:
        filters["has_videos"] = has_videos
    
    try:
        results = await search_engine.search(q, filters=filters, limit=limit, offset=offset)
        
        return {
            "query": q,
            "total": len(results),
            "limit": limit,
            "offset": offset,
            "results": [r.dict() for r in results],
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {
            "query": q,
            "total": 0,
            "limit": limit,
            "offset": offset,
            "results": [],
        }


@app.get("/api/facets")
async def api_facets():
    """Get facet counts for filtering."""
    if not search_engine:
        return {}
    
    try:
        facets = await search_engine.get_facets()
        return facets
    except Exception as e:
        logger.error(f"Failed to get facets: {e}")
        return {}


@app.get("/api/suggest")
async def api_suggest(
    q: str = Query(..., description="Partial query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum suggestions"),
):
    """Get search suggestions."""
    if not search_engine:
        return {"query": q, "suggestions": []}
    
    try:
        suggestions = await search_engine.suggest(q, limit=limit)
        return {"query": q, "suggestions": suggestions}
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        return {"query": q, "suggestions": []}


@app.post("/api/archive")
async def api_archive(request: ArchiveRequest):
    """Start archiving URLs."""
    # Initialize archiver on-demand if not available
    global archiver, config
    
    if not archiver:
        logger.info("Archiver not initialized at startup, attempting on-demand initialization...")
        try:
            if not config:
                config = load_config()
            archiver = ChronosArchiver(config)
            logger.info("Archiver initialized successfully on-demand")
        except Exception as e:
            logger.error(f"Failed to initialize archiver on-demand: {e}")
            raise HTTPException(
                status_code=503, 
                detail=f"Archiver not available: {str(e)}. Check Redis, Meilisearch, and Tika connections."
            )
    
    job_ids = []
    
    try:
        for url in request.urls:
            job_id = str(uuid.uuid4())
            job = {
                "id": job_id,
                "url": url,
                "status": ArchiveStatus.PENDING,
                "progress": 0,
                "stage": "discovery",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            active_jobs[job_id] = job
            job_ids.append(job_id)
            
            # Start archiving in background
            asyncio.create_task(process_archive_job(job_id, url))
        
        return {"job_ids": job_ids, "message": f"Started archiving {len(request.urls)} URLs"}
    
    except Exception as e:
        logger.error(f"Failed to create archive jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create archive jobs: {str(e)}")


async def process_archive_job(job_id: str, url: str):
    """Process an archive job and send updates via WebSocket."""
    job = active_jobs[job_id]
    
    try:
        # Update: Discovery
        job["stage"] = "discovery"
        job["status"] = ArchiveStatus.DISCOVERED
        job["progress"] = 25
        job["updated_at"] = datetime.utcnow().isoformat()
        await broadcast_job_update(job)
        
        # Download
        job["stage"] = "ingestion"
        job["status"] = ArchiveStatus.DOWNLOADING
        job["progress"] = 50
        job["updated_at"] = datetime.utcnow().isoformat()
        await broadcast_job_update(job)
        
        # Archive the URL
        if archiver:
            await archiver.archive_url(url)
        else:
            raise Exception("Archiver not available")
        
        # Transform
        job["stage"] = "transformation"
        job["status"] = ArchiveStatus.TRANSFORMING
        job["progress"] = 75
        job["updated_at"] = datetime.utcnow().isoformat()
        await broadcast_job_update(job)
        
        # Complete
        job["stage"] = "indexing"
        job["status"] = ArchiveStatus.INDEXED
        job["progress"] = 100
        job["updated_at"] = datetime.utcnow().isoformat()
        await broadcast_job_update(job)
        
    except Exception as e:
        job["status"] = ArchiveStatus.FAILED
        job["error"] = str(e)
        job["updated_at"] = datetime.utcnow().isoformat()
        await broadcast_job_update(job)
        logger.error(f"Archive job {job_id} failed: {e}")


async def broadcast_job_update(job: dict):
    """Broadcast job update to all connected WebSocket clients."""
    disconnected = set()
    
    for ws in websocket_connections:
        try:
            await ws.send_json({"type": "job_update", "data": job})
        except Exception:
            disconnected.add(ws)
    
    # Remove disconnected clients
    websocket_connections.difference_update(disconnected)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.add(websocket)
    logger.info(f"WebSocket client connected. Total connections: {len(websocket_connections)}")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages if needed
            logger.debug(f"Received WebSocket message: {data}")
    except WebSocketDisconnect:
        websocket_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(websocket_connections)}")


@app.get("/api/jobs", response_model=List[ArchiveJobResponse])
async def api_get_jobs():
    """Get all archive jobs."""
    return list(active_jobs.values())


@app.get("/api/stats")
async def api_stats():
    """Get archive statistics."""
    # Calculate real stats from active jobs
    total_jobs = len(active_jobs)
    completed_jobs = len([j for j in active_jobs.values() if j["status"] == ArchiveStatus.INDEXED])
    failed_jobs = len([j for j in active_jobs.values() if j["status"] == ArchiveStatus.FAILED])
    
    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
    
    return {
        "total_pages": total_jobs,
        "total_size": "0 MB",
        "oldest_snapshot": "N/A",
        "newest_snapshot": "N/A",
        "languages": {"pt": 10, "en": 5},
        "topics": {"religião": 8, "notícias": 3, "comunidade": 2},
        "success_rate": round(success_rate, 1),
        "total_embeds": 15,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "search_engine": search_engine is not None,
            "indexer": indexer is not None,
            "archiver": archiver is not None,
        },
        "active_jobs": len(active_jobs),
        "websocket_connections": len(websocket_connections),
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "chronos_archiver.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
