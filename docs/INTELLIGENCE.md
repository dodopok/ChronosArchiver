# Motor de Inteligência / Intelligence Engine

O ChronosArchiver inclui um motor de inteligência avançado para análise e extração automática de conteúdo.

ChronosArchiver includes an advanced intelligence engine for automatic content analysis and extraction.

## Funcionalidades / Features

### 1. Detecção de Idiomas / Language Detection

Detecta automaticamente os idiomas presentes no conteúdo com probabilidades.

Automatically detects languages present in content with probabilities.

```python
from chronos_archiver.intelligence import IntelligenceEngine

engine = IntelligenceEngine(config)
analysis = await engine.analyze(transformed_content)

print(analysis.languages)
# [('pt', 0.95), ('en', 0.05)]
```

### 2. Extração de Entidades Nomeadas / Named Entity Extraction

Identifica e extrai entidades como pessoas, organizações, locais, datas e eventos.

Identifies and extracts entities like people, organizations, locations, dates, and events.

```python
print(analysis.entities)
# {
#     "PERSON": ["João Silva", "Maria Santos"],
#     "ORG": ["Diocese Anglicana do Recife", "IEAB"],
#     "LOC": ["Recife", "Pernambuco", "Brasil"],
#     "DATE": ["2009", "abril"],
#     "EVENT": ["Páscoa", "Culto"]
# }
```

### 3. Extração de Palavras-Chave / Keyword Extraction

Extrai automaticamente palavras-chave relevantes do conteúdo.

Automatically extracts relevant keywords from content.

```python
print(analysis.keywords)
# ['diocese anglicana', 'igreja episcopal', 'comunidade', 'culto', 'paróquia']
```

### 4. Classificação de Tópicos / Topic Classification

Classifica o conteúdo em tópicos predefinidos.

Classifies content into predefined topics.

```python
print(analysis.topics)
# ['religião', 'comunidade', 'notícias']
```

### 5. Detecção de Embeds de Mídia / Media Embed Detection

Detecta e extrai automaticamente embeds de vídeos e áudios.

Automatically detects and extracts video and audio embeds.

**Plataformas Suportadas / Supported Platforms:**
- YouTube
- Vimeo
- Dailymotion
- SoundCloud
- Iframes genéricos / Generic iframes

```python
for embed in analysis.media_embeds:
    print(f"{embed.platform}: {embed.url}")
    print(f"  Video ID: {embed.video_id}")
    print(f"  Embed URL: {embed.embed_url}")

# Output:
# YouTube: https://www.youtube.com/watch?v=abc123
#   Video ID: abc123
#   Embed URL: https://www.youtube.com/embed/abc123
```

### 6. Geração de Sumário / Summary Generation

Gera automaticamente um sumário do conteúdo.

Automatically generates a content summary.

```python
summary = engine.generate_summary(text, max_sentences=3)
print(summary)
```

## Integração Apache Tika / Apache Tika Integration

O ChronosArchiver integra Apache Tika para extração avançada de texto e metadados.

ChronosArchiver integrates Apache Tika for advanced text and metadata extraction.

### Formatos Suportados / Supported Formats

- HTML, XML
- PDF
- Microsoft Office (DOC, DOCX, XLS, XLSX, PPT, PPTX)
- OpenDocument (ODT, ODS, ODP)
- Imagens (JPEG, PNG, GIF, TIFF) - com OCR
- E-books (EPUB, MOBI)
- E muitos outros / And many more

### Uso / Usage

```python
from chronos_archiver.tika import TikaExtractor

extractor = TikaExtractor(config)
result = extractor.extract_text(content_bytes)

print(result['text'])  # Extracted text
print(result['metadata'])  # Document metadata
# {
#     'author': 'John Doe',
#     'title': 'Document Title',
#     'creation_date': '2023-01-15',
#     'language': 'pt',
#     'keywords': 'igreja, diocese'
# }
```

## Motor de Busca Avançado / Advanced Search Engine

Integração com Meilisearch para busca avançada.

Meilisearch integration for advanced search.

### Funcionalidades / Features

1. **Busca de Texto Completo / Full-Text Search**
   - Tolerância a erros de digitação / Typo tolerance
   - Busca por relevância / Relevance ranking
   - Destaque de resultados / Result highlighting

2. **Busca com Filtros / Faceted Search**
   - Filtrar por tópico / Filter by topic
   - Filtrar por idioma / Filter by language
   - Filtrar por tipo de mídia / Filter by media type
   - Filtrar por data / Filter by date

3. **Sugestões Automáticas / Auto-Suggestions**
   - Sugestões de busca em tempo real / Real-time search suggestions

### Exemplo / Example

```python
from chronos_archiver.search import SearchEngine

search = SearchEngine(config)

# Simple search
results = await search.search("diocese anglicana")

# Search with filters
results = await search.search(
    "igreja",
    filters={
        "topics": ["religião", "comunidade"],
        "has_videos": True
    },
    limit=20
)

# Get suggestions
suggestions = await search.suggest("dio", limit=5)
print(suggestions)
# ['diocese', 'diocese anglicana', 'diocesano']
```

## Interface Web / Web Interface

O ChronosArchiver inclui uma interface web completa com FastAPI.

ChronosArchiver includes a complete web interface with FastAPI.

### Recursos / Features

- 🔍 **Busca Inteligente / Smart Search** - Busca com tolerância a erros
- 🎥 **Visualização de Embeds / Embed Viewing** - Visualize vídeos diretamente
- 📊 **Estatísticas / Statistics** - Estatísticas do arquivo
- 🌎 **Suporte Multilingual / Multilingual Support** - Português e Inglês
- 📡 **API RESTful** - API completa para integração

### Iniciar / Start

```bash
# Start all services with Docker Compose
docker-compose up -d

# Or run directly
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000
```

Acesse / Access: http://localhost:8000

### Endpoints da API / API Endpoints

#### Buscar / Search
```http
GET /api/search?q=igreja&topics=religião&limit=20
```

#### Facetas / Facets
```http
GET /api/facets
```

#### Sugestões / Suggestions
```http
GET /api/suggest?q=dio
```

#### Estatísticas / Statistics
```http
GET /api/stats
```

## Configuração / Configuration

Edite `config.yaml`:

```yaml
intelligence:
  enable_nlp: true
  enable_entity_extraction: true
  enable_language_detection: true
  enable_embed_detection: true

tika:
  enabled: true
  server_url: "http://localhost:9998"

search:
  meilisearch_host: "http://localhost:7700"
  index_name: "chronos_archive"

api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
```

## Instalar Modelos de Idioma / Install Language Models

### Português / Portuguese
```bash
python -m spacy download pt_core_news_sm
```

### Multilingual
```bash
python -m spacy download xx_ent_wiki_sm
```

## Exemplo Completo / Complete Example

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.search import SearchEngine
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    
    # Initialize engines
    archiver = ChronosArchiver(config)
    intelligence = IntelligenceEngine(config)
    search = SearchEngine(config)
    
    # Archive URL
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    
    # Discovery
    snapshots = await archiver.discovery.find_snapshots(url)
    
    for snapshot in snapshots[:1]:
        # Download
        downloaded = await archiver.ingestion.download(snapshot)
        
        # Transform
        transformed = await archiver.transformation.transform(downloaded)
        
        # Analyze with intelligence engine
        analysis = await intelligence.analyze(transformed)
        
        print(f"Languages: {analysis.languages}")
        print(f"Keywords: {analysis.keywords}")
        print(f"Topics: {analysis.topics}")
        print(f"Entities: {analysis.entities}")
        print(f"Media embeds: {len(analysis.media_embeds)}")
        
        # Index in search engine
        await search.index_content(analysis)
        
        # Search
        results = await search.search("diocese")
        print(f"Found {len(results)} results")
    
    await archiver.shutdown()

asyncio.run(main())
```

## Suporte / Support

Para questões e suporte: / For questions and support:
- GitHub Issues: https://github.com/dodopok/ChronosArchiver/issues
- Email: support@chronosarchiver.dev