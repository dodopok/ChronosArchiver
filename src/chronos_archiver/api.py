"""API module - FastAPI web interface for ChronosArchiver."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from chronos_archiver.config import load_config
from chronos_archiver.indexing import ContentIndexer
from chronos_archiver.search import SearchEngine

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ChronosArchiver API",
    description="API para pesquisa e visualização de conteúdo arquivado / API for searching and viewing archived content",
    version="1.0.0",
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

# Global config and engines
config = None
search_engine = None
indexer = None

# Templates
templates = Jinja2Templates(directory="templates")


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    filters: Optional[dict[str, Any]] = None
    limit: int = 20
    offset: int = 0


class ArchiveRequest(BaseModel):
    """Archive request model."""
    urls: list[str]
    priority: str = "normal"


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    global config, search_engine, indexer
    
    logger.info("Starting ChronosArchiver API...")
    
    # Load configuration
    config = load_config()
    
    # Initialize search engine
    try:
        search_engine = SearchEngine(config)
        logger.info("Search engine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")
    
    # Initialize indexer
    try:
        indexer = ContentIndexer(config)
        logger.info("Indexer initialized")
    except Exception as e:
        logger.error(f"Failed to initialize indexer: {e}")
    
    logger.info("ChronosArchiver API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global indexer
    
    if indexer:
        await indexer.close()
    
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
            .search-box {
                display: flex;
                margin-bottom: 30px;
            }
            input[type="search"] {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px 0 0 10px;
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            input[type="search"]:focus {
                border-color: #667eea;
            }
            button {
                padding: 15px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 0 10px 10px 0;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: background 0.3s;
            }
            button:hover {
                background: #5568d3;
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
            .feature-desc {
                color: #666;
                font-size: 0.9em;
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
            
            <form action="/search" method="get" class="search-box">
                <input type="search" name="q" placeholder="Pesquisar conteúdo arquivado..." required>
                <button type="submit">Buscar</button>
            </form>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🔍</div>
                    <div class="feature-title">Busca Inteligente</div>
                    <div class="feature-desc">Pesquisa com tolerância a erros e relevância</div>
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
                    <div class="feature-desc">Otimizado para português brasileiro</div>
                </div>
            </div>
            
            <div class="api-link">
                <a href="/api/docs" target="_blank">Documentação da API →</a>
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
    """Search archived content.
    
    Pesquisar conteúdo arquivado com suporte a filtros e paginação.
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    # Build filters
    filters = {}
    if topics:
        filters["topics"] = topics.split(",")
    if has_videos is not None:
        filters["has_videos"] = has_videos
    
    # Search
    results = await search_engine.search(q, filters=filters, limit=limit, offset=offset)
    
    return {
        "query": q,
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "results": [r.dict() for r in results],
    }


@app.get("/api/facets")
async def api_facets():
    """Get facet counts for filtering.
    
    Obter contagens de facetas para filtragem.
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    facets = await search_engine.get_facets()
    return facets


@app.get("/api/suggest")
async def api_suggest(
    q: str = Query(..., description="Partial query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum suggestions"),
):
    """Get search suggestions.
    
    Obter sugestões de busca.
    """
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not available")
    
    suggestions = await search_engine.suggest(q, limit=limit)
    return {"query": q, "suggestions": suggestions}


@app.get("/api/stats")
async def api_stats():
    """Get archive statistics.
    
    Obter estatísticas do arquivo.
    """
    if not indexer:
        raise HTTPException(status_code=503, detail="Indexer not available")
    
    # Get database stats
    # This is a placeholder - implement based on your database
    return {
        "total_pages": 0,
        "total_size": "0 MB",
        "oldest_snapshot": "N/A",
        "newest_snapshot": "N/A",
        "languages": {},
        "topics": {},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "search_engine": search_engine is not None,
        "indexer": indexer is not None,
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