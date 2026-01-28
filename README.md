# ChronosArchiver

> Sistema de arquivamento inteligente para preservar e analisar sites da Wayback Machine  
> Intelligent archival system to download and analyze websites from the Internet Archive's Wayback Machine

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Recursos Principais / Key Features

### 📦 Pipeline de 4 Estágios / 4-Stage Pipeline
- **Discovery**: Integração com CDX API para encontrar URLs / CDX API integration
- **Ingestion**: Download assíncrono com retry / Async downloading with retry
- **Transformation**: Reescrita de links e extração de metadados / Link rewriting and metadata extraction
- **Indexing**: Armazenamento e busca / Storage and search

### 🧠 Motor de Inteligência / Intelligence Engine
- **Detecção de Idiomas** / Language Detection
- **Extração de Entidades Nomeadas** (pessoas, organizações, locais) / Named Entity Extraction
- **Extração de Palavras-Chave** / Keyword Extraction  
- **Classificação de Tópicos** / Topic Classification
- **Análise de Sentimento** / Sentiment Analysis

### 🎥 Detecção de Embeds / Embed Detection
- **YouTube** - Detecção automática de vídeos / Automatic video detection
- **Vimeo** - Extração de embeds / Embed extraction
- **Dailymotion** - Suporte completo / Full support
- **SoundCloud** - Áudio embeds / Audio embeds
- **Iframes Genéricos** / Generic iframes

### 🔍 Busca Avançada / Advanced Search
- **Meilisearch Integration** - Busca instantânea / Instant search
- **Tolerância a Erros** / Typo tolerance
- **Busca com Filtros** / Faceted search
- **Destaque de Resultados** / Result highlighting
- **Sugestões Automáticas** / Auto-suggestions

### 🌎 Interface Web / Web Interface
- **FastAPI** - API RESTful moderna / Modern RESTful API
- **Interface de Busca** / Search interface
- **Visualização de Embeds** / Embed viewing
- **Estatísticas** / Statistics dashboard
- **Suporte Bilingual** / Bilingual support (PT/EN)

### 📑 Extração Avançada / Advanced Extraction
- **Apache Tika** - Extração de PDF, Office, imagens / PDF, Office, image extraction
- **OCR** - Reconhecimento de texto em imagens / Text recognition in images
- **Metadados** - Autor, data de criação, etc / Author, creation date, etc.

## 🚀 Quick Start

### Instalação / Installation

```bash
# Clone the repository
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install language models
python -m spacy download pt_core_news_sm  # Portuguese
python -m spacy download xx_ent_wiki_sm   # Multilingual

# Install in development mode
pip install -e .
```

### Iniciar Serviços / Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Services started:
# - Redis (port 6379) - Message queues
# - Meilisearch (port 7700) - Search engine
# - Apache Tika (port 9998) - Text extraction
# - ChronosArchiver API (port 8000) - Web interface
# - Workers - Background processing
```

### Usar / Usage

```bash
# Archive a single URL
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/

# Archive from file
chronos archive --input examples/sample_sites.txt --workers 8

# Start web interface
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000
```

Acesse / Access: **http://localhost:8000**

## 📚 Documentação / Documentation

- **[Guia de Uso / Usage Guide](docs/usage.md)** - Como usar o sistema / How to use
- **[Motor de Inteligência / Intelligence Engine](docs/INTELLIGENCE.md)** - Recursos avançados / Advanced features
- **[Arquitetura / Architecture](docs/architecture.md)** - Design do sistema / System design
- **[API Reference](docs/api.md)** - Referência completa / Complete reference

## 💻 Uso Programático / Programmatic Usage

### Exemplo Básico / Basic Example

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Archive URL
    await archiver.archive_url(
        'https://web.archive.org/web/20090430060114/http://www.dar.org.br/'
    )
    
    await archiver.shutdown()

asyncio.run(main())
```

### Com Análise de Inteligência / With Intelligence Analysis

```python
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.search import SearchEngine

# Initialize engines
intelligence = IntelligenceEngine(config)
search = SearchEngine(config)

# Process content
snapshots = await archiver.discovery.find_snapshots(url)
for snapshot in snapshots:
    downloaded = await archiver.ingestion.download(snapshot)
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

# Search archived content
results = await search.search("diocese anglicana", limit=10)
for result in results:
    print(f"{result.title} - {result.url}")
```

### Detecção de Embeds / Embed Detection

```python
# Analyze content for media embeds
analysis = await intelligence.analyze(transformed)

for embed in analysis.media_embeds:
    if embed.type == "youtube":
        print(f"YouTube Video: {embed.video_id}")
        print(f"  URL: {embed.url}")
        print(f"  Embed: {embed.embed_url}")
    elif embed.type == "vimeo":
        print(f"Vimeo Video: {embed.video_id}")
```

## 🌐 Interface Web / Web Interface

### Página Principal / Home Page

![ChronosArchiver Web Interface](https://via.placeholder.com/800x400.png?text=ChronosArchiver+Web+Interface)

### Endpoints da API / API Endpoints

#### Buscar / Search
```bash
curl "http://localhost:8000/api/search?q=diocese&topics=religião&limit=20"
```

#### Obter Facetas / Get Facets
```bash
curl "http://localhost:8000/api/facets"
```

#### Sugestões / Suggestions
```bash
curl "http://localhost:8000/api/suggest?q=igr"
```

#### Estatísticas / Statistics
```bash
curl "http://localhost:8000/api/stats"
```

### Documentação Interativa / Interactive Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## ⚙️ Configuração / Configuration

Edite `config.yaml`:

```yaml
# Intelligence engine
intelligence:
  enable_nlp: true
  enable_entity_extraction: true
  enable_language_detection: true
  enable_embed_detection: true

# Apache Tika
tika:
  enabled: true
  server_url: "http://localhost:9998"

# Meilisearch
search:
  meilisearch_host: "http://localhost:7700"
  index_name: "chronos_archive"

# Web API
api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  enable_cors: true

# Processing
processing:
  workers: 4
  requests_per_second: 5
  retry_attempts: 3
```

## 📦 Sites de Exemplo / Sample Sites

O projeto inclui URLs de exemplo para teste: / The project includes sample URLs for testing:

```
# Diocese Anglicana do Recife (DAR)
https://web.archive.org/web/20090430060114/http://www.dar.org.br/
https://web.archive.org/web/20120302052501/http://www.dar.org.br/
https://web.archive.org/web/20150406103050/http://dar.org.br/
https://web.archive.org/web/20101223085644/http://dar.ieab.org.br/

# Igreja Episcopal Anglicana do Brasil (IEAB)
https://web.archive.org/web/20041022131803fw_/http://www.ieabrecife.com.br/
https://web.archive.org/web/20050829171410fw_/http://www.ieabweb.org.br/
https://web.archive.org/web/20051125104316fw_/http://www.ieabweb.org.br/dar/
```

## 🔧 Recursos Avançados / Advanced Features

### Extração com Apache Tika / Extraction with Apache Tika

```python
from chronos_archiver.tika import TikaExtractor

extractor = TikaExtractor(config)
result = extractor.extract_text(pdf_content)

print(result['text'])  # Extracted text
print(result['metadata'])  # Author, date, etc.
```

### Busca Avançada / Advanced Search

```python
# Search with filters
results = await search.search(
    "igreja",
    filters={
        "topics": ["religião", "comunidade"],
        "languages": ["pt"],
        "has_videos": True
    },
    limit=50,
    offset=0
)

# Get facet counts
facets = await search.get_facets()
print(facets['topics'])  # Topic distribution
print(facets['languages'])  # Language distribution
```

### Processamento em Lote / Batch Processing

```python
# Process multiple URLs concurrently
urls = [
    "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
    "https://web.archive.org/web/20120302052501/http://www.dar.org.br/",
    "https://web.archive.org/web/20150406103050/http://dar.org.br/",
]

await archiver.archive_urls(urls)
```

## 🐞 Testes / Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=chronos_archiver --cov-report=html

# Run specific tests
pytest tests/test_intelligence.py -v
pytest tests/integration/ -v
```

## 📦 Docker

### Usando Docker Compose / Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f worker

# Scale workers
docker-compose up -d --scale worker=4

# Stop services
docker-compose down
```

### Build Manual / Manual Build

```bash
# Build image
docker build -t chronos-archiver .

# Run container
docker run -d \
  --name chronos \
  -p 8000:8000 \
  -v $(pwd)/archive:/app/archive \
  -v $(pwd)/config.yaml:/app/config.yaml \
  chronos-archiver
```

## 🎓 Casos de Uso / Use Cases

### 1. Pesquisa Histórica / Historical Research
Arquive e analise versões históricas de sites para pesquisa acadêmica.

Archive and analyze historical versions of websites for academic research.

### 2. Preservação Digital / Digital Preservation
Preserve conteúdo importante que pode desaparecer da web.

Preserve important content that may disappear from the web.

### 3. Análise de Conteúdo / Content Analysis
Analise automaticamente conteúdo arquivado com NLP e inteligência artificial.

Automatically analyze archived content with NLP and AI.

### 4. Extração de Mídia / Media Extraction
Detecte e catalogue vídeos e áudios embarcados em sites arquivados.

Detect and catalog embedded videos and audio in archived sites.

## 📊 Estrutura do Projeto / Project Structure

```
ChronosArchiver/
├── src/chronos_archiver/
│   ├── __init__.py
│   ├── discovery.py          # Stage 1: URL discovery
│   ├── ingestion.py          # Stage 2: Content download
│   ├── transformation.py     # Stage 3: Content transformation
│   ├── indexing.py           # Stage 4: Storage & indexing
│   ├── intelligence.py       # 🧠 Intelligence engine
│   ├── search.py             # 🔍 Meilisearch integration
│   ├── tika.py               # 📑 Apache Tika integration
│   ├── api.py                # 🌐 FastAPI web interface
│   ├── queue_manager.py      # Queue management
│   ├── models.py             # Data models
│   ├── config.py             # Configuration
│   ├── cli.py                # CLI interface
│   └── utils.py              # Utilities
├── tests/                    # 🧪 Test suite
├── docs/                     # 📚 Documentation
├── examples/                 # 💡 Usage examples
├── docker-compose.yml        # 🐳 Docker configuration
├── requirements.txt          # Dependencies
└── config.yaml.example       # Sample configuration
```

## 🌟 Novos Recursos / New Features

### v1.1.0 (Current)

✅ Motor de inteligência com NLP / Intelligence engine with NLP  
✅ Detecção de embeds (YouTube, Vimeo, etc.) / Embed detection  
✅ Integração Meilisearch / Meilisearch integration  
✅ Interface web com FastAPI / FastAPI web interface  
✅ Integração Apache Tika / Apache Tika integration  
✅ Suporte completo a português / Full Portuguese support  
✅ Extração de entidades nomeadas / Named entity extraction  
✅ Classificação de tópicos / Topic classification  
✅ Busca com filtros e facetas / Faceted search  

## 🗺️ Roadmap

- [ ] Análise de sentimento / Sentiment analysis
- [ ] Suporte a mais plataformas de vídeo / More video platform support
- [ ] Dashboard de visualização / Visualization dashboard
- [ ] Exportação WARC / WARC format export
- [ ] API GraphQL / GraphQL API
- [ ] Arquivamento incremental / Incremental archiving
- [ ] Suporte a mais idiomas / More language support

## 🤝 Contribuindo / Contributing

Contribuições são bem-vindas! / Contributions are welcome!

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes. / See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 Licença / License

MIT License - veja [LICENSE](LICENSE) para detalhes. / See [LICENSE](LICENSE) for details.

## 💬 Suporte / Support

- **Issues**: [GitHub Issues](https://github.com/dodopok/ChronosArchiver/issues)
- **Discussões / Discussions**: [GitHub Discussions](https://github.com/dodopok/ChronosArchiver/discussions)
- **Email**: support@chronosarchiver.dev

## 🚀 Agradecimentos / Acknowledgments

- [Internet Archive](https://archive.org/) - Wayback Machine
- [Meilisearch](https://www.meilisearch.com/) - Search engine
- [Apache Tika](https://tika.apache.org/) - Content extraction
- [spaCy](https://spacy.io/) - NLP library
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

---

**Feito com ❤️ por Douglas Araujo / Made with ❤️ by Douglas Araujo**