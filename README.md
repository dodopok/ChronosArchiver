# 🕒 ChronosArchiver

> **Sistema Completo de Arquivamento Inteligente com Interface Web Moderna**  
> **Complete Intelligent Archiving System with Modern Web Interface**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.2-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.2-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🌟 Visão Geral / Overview

ChronosArchiver é um sistema completo para arquivar, analisar e pesquisar sites históricos da Wayback Machine com:

ChronosArchiver is a complete system to archive, analyze, and search historical websites from the Wayback Machine with:

- 📦 **Pipeline de 4 Estágios** / 4-Stage Async Pipeline
- 🧠 **Motor de Inteligência com NLP** / Intelligence Engine with NLP
- 🎥 **Detecção de Embeds** (YouTube, Vimeo) / Embed Detection
- 🔍 **Busca Avançada** com Meilisearch / Advanced Search
- 🌐 **Interface Web React** / React Web Interface
- 📑 **Extração Apache Tika** / Apache Tika Extraction
- 🇧🇷 **Suporte Completo a Português** / Full Portuguese Support

---

## 🚀 Demonstração Rápida / Quick Demo

```bash
# 1. Iniciar todos os serviços / Start all services
docker-compose up -d

# 2. Acessar interface web / Access web interface
open http://localhost:3000

# 3. Arquivar um site / Archive a site
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

**Serviços disponíveis / Available services:**
- 🌐 **Frontend React**: http://localhost:3000
- 🔧 **API Backend**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/api/docs
- 🔍 **Meilisearch**: http://localhost:7700

---

## ✨ Recursos Principais / Key Features

### 📦 Pipeline de Arquivamento / Archiving Pipeline

```
Discovery → Ingestion → Transformation → Indexing
   🔍         📥            ♻️              💾
```

1. **Discovery** - Encontra snapshots via CDX API / Finds snapshots via CDX API
2. **Ingestion** - Download assíncrono com retry / Async download with retry
3. **Transformation** - Reescreve links e extrai dados / Rewrites links and extracts data
4. **Indexing** - Armazena e indexa / Stores and indexes

### 🧠 Motor de Inteligência / Intelligence Engine

```python
analysis = await intelligence.analyze(content)

print(f"Idiomas: {analysis.languages}")  # [('pt', 0.95), ('en', 0.05)]
print(f"Entidades: {analysis.entities}")  # {'ORG': ['Diocese...'], 'LOC': ['Recife']}
print(f"Palavras-chave: {analysis.keywords}")  # ['diocese', 'igreja', ...]
print(f"Tópicos: {analysis.topics}")  # ['religião', 'comunidade']
print(f"Vídeos: {len(analysis.media_embeds)}")  # 5
```

**Recursos / Features:**
- ✅ Detecção automática de idioma / Automatic language detection
- ✅ Extração de entidades (pessoas, organizações, locais) / Entity extraction
- ✅ Extração de palavras-chave / Keyword extraction
- ✅ Classificação de tópicos / Topic classification
- ✅ Geração de sumário / Summary generation

### 🎥 Detecção de Embeds de Mídia / Media Embed Detection

**Plataformas suportadas / Supported platforms:**

| Plataforma | Detecção | Extração de ID | Status |
|------------|----------|---------------|--------|
| YouTube | ✅ | ✅ | Complete |
| Vimeo | ✅ | ✅ | Complete |
| Dailymotion | ✅ | ✅ | Complete |
| SoundCloud | ✅ | - | Complete |
| Iframes Genéricos | ✅ | - | Complete |

```python
for embed in analysis.media_embeds:
    print(f"{embed.platform}: {embed.url}")
    print(f"  ID: {embed.video_id}")
    print(f"  Embed: {embed.embed_url}")
```

### 🔍 Busca Avançada / Advanced Search

**Powered by Meilisearch:**
- ⚡ **Instant search** (< 50ms)
- 🔤 **Typo tolerance** - Encontra mesmo com erros / Finds even with typos
- 🏷️ **Faceted search** - Filtros por tópico, idioma, mídia / Filter by topic, language, media
- 🔆 **Highlighting** - Destaque dos termos buscados / Highlights search terms
- 🇧🇷 **Portuguese optimized** - Otimizado para português

### 🌐 Interface Web React / React Web Interface

**Modern, responsive UI with:**

| Feature | Description | Status |
|---------|-------------|--------|
| 📊 **Dashboard** | Real-time monitoring with WebSocket | ✅ |
| 🔍 **Search** | Smart search with auto-suggestions | ✅ |
| 📦 **Archive** | URL management and batch upload | ✅ |
| 🎥 **Media Browser** | View embedded videos/audio | ✅ |
| 📊 **Statistics** | Charts and metrics | ✅ |
| 🌑 **Dark/Light Theme** | Theme toggle | ✅ |
| 📱 **Responsive** | Mobile-first design | ✅ |

---

## 💻 Instalação / Installation

### Optião 1: Docker Compose (Recomendado / Recommended)

```bash
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver
docker-compose up -d
```

**Isso inicia / This starts:**
- ✅ Redis (port 6379)
- ✅ Meilisearch (port 7700)
- ✅ Apache Tika (port 9998)
- ✅ PostgreSQL (port 5432)
- ✅ FastAPI Backend (port 8000)
- ✅ React Frontend (port 3000)
- ✅ Workers (background)

### Optião 2: Instalação Manual / Manual Installation

#### Backend

```bash
# Python dependencies
pip install -r requirements.txt
pip install -e .

# Language models
python -m spacy download pt_core_news_sm
python -m spacy download xx_ent_wiki_sm

# Start services
redis-server &
meilisearch --http-addr 127.0.0.1:7700 &
docker run -d -p 9998:9998 apache/tika:latest

# Start API
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Uso / Usage

### Via Interface Web / Via Web Interface

1. **Acesse / Access**: http://localhost:3000
2. **Vá para "Archive"** / Go to "Archive"
3. **Adicione URLs** / Add URLs
4. **Clique em "Archive"** / Click "Archive"
5. **Monitore o progresso** no Dashboard / Monitor progress on Dashboard
6. **Busque o conteúdo** na página Search / Search content on Search page

### Via CLI

```bash
# Archive single URL
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/

# Archive from file
chronos archive --input examples/sample_sites.txt --workers 8

# Start workers
chronos workers start --count 4
```

### Via API

```bash
# Search
curl "http://localhost:8000/api/search?q=diocese&topics=religi%C3%A3o"

# Archive URLs
curl -X POST http://localhost:8000/api/archive \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://web.archive.org/web/..."], "priority": "normal"}'

# Get statistics
curl http://localhost:8000/api/stats
```

### Via Python

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.search import SearchEngine
from chronos_archiver.config import load_config

async def main():
    config = load_config()
    archiver = ChronosArchiver(config)
    intelligence = IntelligenceEngine(config)
    search = SearchEngine(config)
    
    # Archive with intelligence
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    await archiver.archive_url(url, enable_intelligence=True)
    
    # Search
    results = await search.search("diocese", limit=10)
    for result in results:
        print(f"{result.title}: {result.snippet}")
    
    await archiver.shutdown()

asyncio.run(main())
```

---

## 🏛️ Arquitetura / Architecture

### Stack Completo / Full Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                              │
│   React + TypeScript + Material-UI + WebSocket + Recharts        │
│                     http://localhost:3000                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                            REST API + WebSocket
                                    │
┌─────────────────────────────────────────────────────────────────────│
│                        Backend Layer                              │
│        FastAPI + ChronosArchiver + Intelligence Engine           │
│                     http://localhost:8000                          │
└─────────────────────────────────────────────────────────────────────┘
            │               │               │               │
            v               v               v               v
       ┌────────┐   ┌───────────┐   ┌────────┐   ┌────────────┐
       │ Redis  │   │Meilisearch│   │  Tika  │   │  PostgreSQL│
       │  :6379 │   │   :7700   │   │ :9998 │   │    :5432   │
       └────────┘   └───────────┘   └────────┘   └────────────┘
```

---

## 📱 Screenshots da Interface / Interface Screenshots

### Dashboard - Monitoramento em Tempo Real
- 📊 Pipeline monitor com progress bars
- 📈 Estatísticas em tempo real
- 🔔 Notificações de jobs

### Search - Busca Inteligente
- 🔍 Auto-complete com suggestions
- 🏷️ Filtros por tópico e idioma
- 🎯 Resultados com highlighting

### Archive - Gerenciamento de URLs
- ➕ Adicionar URLs manualmente
- 📄 Upload de arquivos .txt/.csv
- 📤 Drag & drop support

### Media Browser - Galeria de Mídia
- 🎥 Grid de vídeos com thumbnails
- ▶️ Player embutido
- 🏷️ Filtros por plataforma

---

## 🛠️ Stack Tecnológico / Technology Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **Vite** - Build tool
- **React Query** - Server state
- **Zustand** - Client state
- **Socket.io** - WebSocket
- **Recharts** - Data visualization
- **React Router** - Navigation

### Backend
- **Python 3.8+** - Language
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **spaCy** - NLP
- **langdetect** - Language detection
- **BeautifulSoup** - HTML parsing
- **aiohttp** - Async HTTP

### Infrastructure
- **Redis** - Message queues
- **Meilisearch** - Search engine
- **Apache Tika** - Text extraction
- **PostgreSQL** - Database
- **Docker** - Containerization
- **Nginx** - Frontend server

---

## 📚 Documentação / Documentation

### Português 🇧🇷
- **[Tutorial Completo](docs/TUTORIAL_PT.md)** - Guia passo a passo
- **[Motor de Inteligência](docs/INTELLIGENCE.md)** - Recursos avançados
- **[Guia de Instalação](INSTALL.md)** - Instalação detalhada
- **[Frontend](frontend/README.md)** - Documentação React

### English 🇬🇧
- **[Architecture Guide](docs/architecture.md)** - System design
- **[API Reference](docs/api.md)** - Complete API docs
- **[Usage Guide](docs/usage.md)** - How to use
- **[Features List](FEATURES.md)** - All features

---

## 🎯 Sites de Exemplo / Sample Sites

### Diocese Anglicana do Recife (DAR)
```
https://web.archive.org/web/20090430060114/http://www.dar.org.br/
https://web.archive.org/web/20120302052501/http://www.dar.org.br/
https://web.archive.org/web/20150406103050/http://dar.org.br/
https://web.archive.org/web/20101223085644/http://dar.ieab.org.br/
```

### Igreja Episcopal Anglicana do Brasil (IEAB)
```
https://web.archive.org/web/20041022131803fw_/http://www.ieabrecife.com.br/
https://web.archive.org/web/20050829171410fw_/http://www.ieabweb.org.br/
https://web.archive.org/web/20051125104316fw_/http://www.ieabweb.org.br/dar/
```

---

## 🧪 Testes / Testing

### Backend
```bash
pytest
pytest --cov=chronos_archiver --cov-report=html
```

### Frontend
```bash
cd frontend
npm test
npm run test:coverage
```

---

## 🔐 Recursos de Produção / Production Features

✅ Error handling e retry logic  
✅ Rate limiting configuravel  
✅ WebSocket para updates em tempo real  
✅ Compressão de conteúdo  
✅ Health checks  
✅ Logging estruturado  
✅ Múltiplos workers escaláveis  
✅ Docker & Docker Compose  
✅ CI/CD com GitHub Actions  
✅ Responsive mobile design  

---

## 🗺️ Roadmap

### v1.2 (Próxima / Next)
- [ ] Análise de sentimento / Sentiment analysis
- [ ] Exportação WARC / WARC export
- [ ] Timeline visualization
- [ ] Mais plataformas de vídeo / More video platforms
- [ ] Mobile app

### v2.0 (Futuro / Future)
- [ ] Machine learning para classificação / ML classification
- [ ] GraphQL API
- [ ] Real-time archiving
- [ ] Blockchain verification

---

## 🤝 Contribuindo / Contributing

Contribuições são bem-vindas! / Contributions welcome!

Veja [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 Licença / License

MIT License - [LICENSE](LICENSE)

---

## 💬 Suporte / Support

- **Issues**: [GitHub Issues](https://github.com/dodopok/ChronosArchiver/issues)
- **Discussões**: [GitHub Discussions](https://github.com/dodopok/ChronosArchiver/discussions)
- **Email**: support@chronosarchiver.dev

---

## 🏆 Agradecimentos / Acknowledgments

- [Internet Archive](https://archive.org/) - Wayback Machine
- [Meilisearch](https://www.meilisearch.com/) - Search engine
- [Apache Tika](https://tika.apache.org/) - Text extraction
- [spaCy](https://spacy.io/) - NLP library
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend library
- [Material-UI](https://mui.com/) - UI components

---

**🌟 Sistema Completo e Produção-Ready / Complete Production-Ready System 🌟**

**Desenvolvido com ❤️ por Douglas Araujo**  
**Developed with ❤️ by Douglas Araujo**