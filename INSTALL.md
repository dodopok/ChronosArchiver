# Guia de Instalação / Installation Guide

## ChronosArchiver - Sistema Completo de Arquivamento Inteligente

### 💻 Pré-requisitos / Prerequisites

- **Python**: 3.8 ou superior / 3.8 or higher
- **Redis**: Para filas de mensagens / For message queues
- **Meilisearch**: Para busca avançada / For advanced search
- **Apache Tika**: Para extração de texto / For text extraction
- **Docker** (opcional / optional): Para deployment simplificado / For simplified deployment

---

## Método 1: Instalação com Docker (Recomendado) / Docker Installation (Recommended)

### Passo 1: Clone o Repositório / Clone Repository

```bash
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver
```

### Passo 2: Configure / Configure

```bash
# Copy example configuration
cp config.yaml.example config.yaml

# Edit configuration as needed
nano config.yaml
```

### Passo 3: Inicie Todos os Serviços / Start All Services

```bash
docker-compose up -d
```

Isso iniciará / This will start:
- ✅ **Redis** (porta/port 6379) - Gerenciamento de filas / Queue management
- ✅ **Meilisearch** (porta/port 7700) - Motor de busca / Search engine
- ✅ **Apache Tika** (porta/port 9998) - Extração de texto / Text extraction
- ✅ **ChronosArchiver API** (porta/port 8000) - Interface web / Web interface
- ✅ **Workers** - Processamento em background / Background processing

### Passo 4: Verifique os Serviços / Check Services

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Test API
curl http://localhost:8000/health
```

### Passo 5: Acesse a Interface Web / Access Web Interface

Abra seu navegador em / Open your browser at: **http://localhost:8000**

---

## Método 2: Instalação Manual / Manual Installation

### Passo 1: Instalar Dependências do Sistema / Install System Dependencies

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    python3.8 \
    python3-pip \
    python3-venv \
    redis-server \
    build-essential \
    libxml2-dev \
    libxslt1-dev
```

#### macOS

```bash
brew install python@3.8 redis
```

#### Windows

1. Instale Python 3.8+ de [python.org](https://www.python.org/downloads/)
2. Instale Redis usando WSL ou [Memurai](https://www.memurai.com/)

### Passo 2: Clone e Configure o Ambiente Virtual / Clone and Setup Virtual Environment

```bash
# Clone repository
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Passo 3: Instalar Dependências Python / Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Passo 4: Instalar Modelos de Idioma / Install Language Models

```bash
# Portuguese model (recommended)
python -m spacy download pt_core_news_sm

# Multilingual model
python -m spacy download xx_ent_wiki_sm

# Optional: Larger Portuguese model for better accuracy
python -m spacy download pt_core_news_lg
```

### Passo 5: Instalar Serviços Externos / Install External Services

#### Redis

```bash
# Ubuntu/Debian
sudo systemctl start redis-server
sudo systemctl enable redis-server

# macOS
brew services start redis

# Verify
redis-cli ping  # Should return: PONG
```

#### Meilisearch

```bash
# Download and install
curl -L https://install.meilisearch.com | sh

# Run Meilisearch
./meilisearch --http-addr 127.0.0.1:7700

# Or use Docker
docker run -d -p 7700:7700 \
  -v $(pwd)/meili_data:/meili_data \
  getmeili/meilisearch:v1.5
```

#### Apache Tika

```bash
# Download Tika server
wget https://dlcdn.apache.org/tika/2.9.1/tika-server-standard-2.9.1.jar

# Run Tika server
java -jar tika-server-standard-2.9.1.jar

# Or use Docker
docker run -d -p 9998:9998 apache/tika:latest
```

### Passo 6: Configurar / Configure

```bash
# Copy example configuration
cp config.yaml.example config.yaml

# Initialize project
chronos init

# Edit configuration
nano config.yaml
```

### Passo 7: Testar Instalação / Test Installation

```bash
# Test CLI
chronos --help

# Validate configuration
chronos validate-config

# Run tests
pytest tests/ -v
```

---

## Configuração / Configuration

### Configurar URLs dos Serviços / Configure Service URLs

Edite `config.yaml`:

```yaml
# Queue backend
queue:
  backend: "redis"
  redis_url: "redis://localhost:6379/0"

# Search engine
search:
  meilisearch_host: "http://localhost:7700"
  # meilisearch_api_key: "your_api_key"  # Optional
  index_name: "chronos_archive"

# Text extraction
tika:
  enabled: true
  server_url: "http://localhost:9998"

# Intelligence engine
intelligence:
  enable_nlp: true
  enable_entity_extraction: true
  enable_language_detection: true
  enable_embed_detection: true

# Web API
api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
```

### Configurar Banco de Dados / Configure Database

#### SQLite (Desenvolvimento / Development)

```yaml
database:
  type: "sqlite"
  sqlite_path: "./archive/chronos.db"
```

#### PostgreSQL (Produção / Production)

```yaml
database:
  type: "postgresql"
  postgresql_url: "postgresql://user:password@localhost:5432/chronos"
  pool_size: 10
  max_overflow: 20
```

---

## Usando o Sistema / Using the System

### 1. Iniciar Serviços / Start Services

#### Com Docker / With Docker

```bash
docker-compose up -d
```

#### Manual

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Meilisearch
./meilisearch --http-addr 127.0.0.1:7700

# Terminal 3: Start Tika
java -jar tika-server-standard-2.9.1.jar

# Terminal 4: Start Workers
chronos workers start --count 4

# Terminal 5: Start Web API
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Arquivar URLs / Archive URLs

```bash
# Single URL
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/

# From file
chronos archive --input examples/sample_sites.txt

# With multiple workers
chronos archive --input urls.txt --workers 8
```

### 3. Acessar Interface Web / Access Web Interface

Abra / Open: **http://localhost:8000**

API Docs: **http://localhost:8000/api/docs**

### 4. Buscar Conteúdo / Search Content

```bash
# Via CLI
chronos search "diocese anglicana"

# Via API
curl "http://localhost:8000/api/search?q=diocese&topics=religi%C3%A3o"

# Via Python
from chronos_archiver.search import SearchEngine
from chronos_archiver.config import load_config

config = load_config()
search = SearchEngine(config)
results = await search.search("diocese", limit=10)
```

---

## Solução de Problemas / Troubleshooting

### Redis não conecta / Redis not connecting

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis         # macOS
```

### Meilisearch não inicia / Meilisearch not starting

```bash
# Check if port is available
lsof -i :7700

# Start Meilisearch with explicit host
./meilisearch --http-addr 0.0.0.0:7700
```

### Tika não responde / Tika not responding

```bash
# Check Java version (needs Java 11+)
java -version

# Test Tika
curl http://localhost:9998/tika

# Restart Tika
pkill -f tika-server
java -jar tika-server-standard-2.9.1.jar
```

### Modelos spaCy não encontrados / spaCy models not found

```bash
# Install Portuguese model
python -m spacy download pt_core_news_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('pt_core_news_sm'); print('OK')"
```

### Erro de memória / Out of memory

```yaml
# Reduce in config.yaml
processing:
  workers: 2
  concurrent_requests: 5
  batch_size: 5
```

---

## Próximos Passos / Next Steps

1. ✅ Leia a [documentação completa](docs/) / Read the [complete documentation](docs/)
2. ✅ Explore os [exemplos](examples/) / Explore the [examples](examples/)
3. ✅ Execute os testes / Run the tests: `pytest`
4. ✅ Configure para produção / Configure for production
5. ✅ Contribua com o projeto / Contribute to the project

---

## Recursos Adicionais / Additional Resources

- 📚 [Documentação](docs/)
- 💻 [Exemplos de Uso](examples/)
- 🐛 [Reportar Issues](https://github.com/dodopok/ChronosArchiver/issues)
- 💬 [Discussões](https://github.com/dodopok/ChronosArchiver/discussions)
- ✉️ [Email](mailto:support@chronosarchiver.dev)

---

**Feito com ❤️ por Douglas Araujo**