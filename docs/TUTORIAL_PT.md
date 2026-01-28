# Tutorial Completo do ChronosArchiver

## Guia passo a passo para arquivar e analisar sites históricos

---

## 🎯 Objetivo

Este tutorial mostra como usar o ChronosArchiver para arquivar sites históricos da Wayback Machine com todas as funcionalidades avançadas:

- 📦 Download de sites completos
- 🧠 Análise inteligente de conteúdo
- 🎥 Detecção de vídeos do YouTube/Vimeo
- 🔍 Busca avançada com Meilisearch
- 🌐 Interface web para visualização

---

## Parte 1: Instalação Completa

### 1.1. Instalar com Docker (Mais Fácil)

```bash
# Clone o repositório
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# Inicie todos os serviços
docker-compose up -d

# Verifique os serviços
docker-compose ps
```

Pronto! Todos os serviços estão rodando:
- ✅ Redis na porta 6379
- ✅ Meilisearch na porta 7700
- ✅ Apache Tika na porta 9998
- ✅ API Web na porta 8000
- ✅ Workers processando em background

### 1.2. Ou Instalar Manualmente

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt
pip install -e .

# 3. Instalar modelos de idioma
python -m spacy download pt_core_news_sm
python -m spacy download xx_ent_wiki_sm

# 4. Iniciar serviços
redis-server &  # Redis
meilisearch --http-addr 127.0.0.1:7700 &  # Meilisearch
docker run -d -p 9998:9998 apache/tika:latest  # Tika
```

---

## Parte 2: Primeiro Arquivamento

### 2.1. Arquivar uma Única URL

```bash
# Arquivar a Diocese Anglicana do Recife (2009)
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

O que acontece:
1. 🔍 **Discovery**: Encontra o snapshot na Wayback Machine
2. 📥 **Ingestion**: Baixa o conteúdo HTML
3. ♻️ **Transformation**: Reescreve links e extrai metadados
4. 🧠 **Intelligence**: Analisa conteúdo (idioma, entidades, embeds)
5. 💾 **Indexing**: Salva no disco e indexa no Meilisearch

### 2.2. Ver o Resultado

```bash
# Verificar arquivos criados
ls -lh archive/content/2009/04/30/

# Ver metadados no banco de dados
sqlite3 archive/chronos.db "SELECT url, title FROM archived_pages LIMIT 1;"
```

---

## Parte 3: Arquivamento em Lote

### 3.1. Criar Lista de URLs

Crie um arquivo `meus_sites.txt`:

```
# Sites históricos da Diocese e IEAB
https://web.archive.org/web/20090430060114/http://www.dar.org.br/
https://web.archive.org/web/20120302052501/http://www.dar.org.br/
https://web.archive.org/web/20150406103050/http://dar.org.br/
https://web.archive.org/web/20101223085644/http://dar.ieab.org.br/
```

### 3.2. Arquivar em Lote

```bash
# Arquivar com 8 workers
chronos archive --input meus_sites.txt --workers 8
```

### 3.3. Acompanhar Progresso

```bash
# Em outro terminal, veja os logs
tail -f logs/chronos.log

# Ou com Docker
docker-compose logs -f worker
```

---

## Parte 4: Análise Inteligente de Conteúdo

### 4.1. Analisar Conteúdo com Python

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def analisar_site():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # URL para analisar
    url = "https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
    
    # Descobrir snapshots
    snapshots = await archiver.discovery.find_snapshots(url)
    snapshot = snapshots[0]
    
    # Baixar
    downloaded = await archiver.ingestion.download(snapshot)
    
    # Transformar
    transformed = await archiver.transformation.transform(downloaded)
    
    # ANALISAR COM MOTOR DE INTELIGÊNCIA
    analysis = await archiver.intelligence.analyze(transformed)
    
    # Mostrar resultados
    print("\n=== ANÁLISE DE CONTEÚDO ===")
    print(f"\n🌎 Idiomas Detectados:")
    for lang, prob in analysis.languages:
        print(f"  - {lang}: {prob*100:.1f}%")
    
    print(f"\n📝 Palavras-Chave:")
    for keyword in analysis.keywords[:10]:
        print(f"  - {keyword}")
    
    print(f"\n🏷️ Tópicos:")
    for topic in analysis.topics:
        print(f"  - {topic}")
    
    print(f"\n👥 Entidades Encontradas:")
    for entity_type, entities in analysis.entities.items():
        if entities:
            print(f"  {entity_type}:")
            for entity in entities[:5]:
                print(f"    - {entity}")
    
    print(f"\n🎥 Vídeos/Mídia Embarcados: {len(analysis.media_embeds)}")
    for embed in analysis.media_embeds:
        print(f"  - {embed.platform}: {embed.url}")
    
    # Indexar na busca
    await archiver.search.index_content(analysis)
    
    await archiver.shutdown()

asyncio.run(analisar_site())
```

### 4.2. Executar o Script

```bash
python meu_script.py
```

Saída esperada:
```
=== ANÁLISE DE CONTEÚDO ===

🌎 Idiomas Detectados:
  - pt: 95.2%
  - en: 4.8%

📝 Palavras-Chave:
  - diocese anglicana
  - igreja episcopal
  - recife
  - comunidade
  - paróquia

🏷️ Tópicos:
  - religião
  - comunidade

👥 Entidades Encontradas:
  ORG:
    - Diocese Anglicana do Recife
    - IEAB
  LOC:
    - Recife
    - Pernambuco
```

---

## Parte 5: Detecção de Vídeos e Embeds

### 5.1. Detectar Vídeos do YouTube

```python
import asyncio
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.config import load_config

async def detectar_videos():
    config = load_config()
    engine = IntelligenceEngine(config)
    
    # HTML com embeds
    html = '''
    <html>
    <body>
        <h1>Página com Vídeos</h1>
        
        <!-- YouTube -->
        <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>
        
        <!-- Vimeo -->
        <iframe src="https://player.vimeo.com/video/123456789"></iframe>
        
        <!-- Link para vídeo -->
        <a href="https://www.youtube.com/watch?v=abc123">Assista</a>
    </body>
    </html>
    '''
    
    # Extrair embeds
    embeds = engine._extract_embeds(html)
    
    print(f"\n🎥 Encontrados {len(embeds)} embeds:\n")
    
    for embed in embeds:
        print(f"Plataforma: {embed.platform}")
        print(f"Tipo: {embed.type}")
        print(f"URL Original: {embed.url}")
        print(f"URL Embed: {embed.embed_url}")
        if embed.video_id:
            print(f"ID do Vídeo: {embed.video_id}")
        print()

asyncio.run(detectar_videos())
```

Saída:
```
🎥 Encontrados 3 embeds:

Plataforma: YouTube
Tipo: youtube
URL Original: https://www.youtube.com/watch?v=dQw4w9WgXcQ
URL Embed: https://www.youtube.com/embed/dQw4w9WgXcQ
ID do Vídeo: dQw4w9WgXcQ

Plataforma: Vimeo
Tipo: vimeo
URL Original: https://vimeo.com/123456789
URL Embed: https://player.vimeo.com/video/123456789
ID do Vídeo: 123456789
```

---

## Parte 6: Busca Avançada

### 6.1. Busca Simples

```python
import asyncio
from chronos_archiver.search import SearchEngine
from chronos_archiver.config import load_config

async def buscar():
    config = load_config()
    search = SearchEngine(config)
    
    # Buscar
    resultados = await search.search("diocese anglicana", limit=10)
    
    print(f"\n🔍 Encontrados {len(resultados)} resultados:\n")
    
    for i, resultado in enumerate(resultados, 1):
        print(f"{i}. {resultado.title}")
        print(f"   URL: {resultado.original_url}")
        print(f"   Data: {resultado.timestamp}")
        print(f"   Score: {resultado.score:.2f}")
        print(f"   Snippet: {resultado.snippet[:100]}...")
        print()

asyncio.run(buscar())
```

### 6.2. Busca com Filtros

```python
# Buscar apenas conteúdo religioso com vídeos
resultados = await search.search(
    "igreja",
    filters={
        "topics": ["religião"],
        "has_videos": True,
        "languages": ["pt"]
    },
    limit=20
)

print(f"Encontrados {len(resultados)} páginas religiosas com vídeos")
```

### 6.3. Obter Estatísticas

```python
# Ver distribuição de tópicos
facets = await search.get_facets()

print("\nTópicos no arquivo:")
for topic, count in facets.get('topics', {}).items():
    print(f"  {topic}: {count} páginas")

print("\nIdiomas no arquivo:")
for lang, count in facets.get('languages', {}).items():
    print(f"  {lang}: {count} páginas")
```

---

## Parte 7: Interface Web

### 7.1. Iniciar a API Web

```bash
# Com Docker (já está rodando)
docker-compose up -d

# Ou manualmente
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000 --reload
```

### 7.2. Acessar a Interface

Abra no navegador:

- **Página Principal**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/api/docs
- **Documentação ReDoc**: http://localhost:8000/api/redoc

### 7.3. Usar a API REST

#### Buscar

```bash
curl "http://localhost:8000/api/search?q=diocese&limit=5"
```

#### Buscar com Filtros

```bash
curl "http://localhost:8000/api/search?q=igreja&topics=religi%C3%A3o&has_videos=true"
```

#### Obter Facetas

```bash
curl "http://localhost:8000/api/facets"
```

#### Sugestões de Busca

```bash
curl "http://localhost:8000/api/suggest?q=igre"
```

Resposta:
```json
{
  "query": "igre",
  "suggestions": [
    "igreja",
    "igreja episcopal",
    "igreja anglicana"
  ]
}
```

---

## Parte 8: Casos de Uso Reais

### 8.1. Arquivar Histórico Completo de um Site

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def arquivar_historico():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Descobrir TODOS os snapshots de um site
    print("Descobrindo snapshots...")
    snapshots = await archiver.discovery.find_snapshots("http://www.dar.org.br/")
    
    print(f"Encontrados {len(snapshots)} snapshots históricos")
    print(f"Período: {snapshots[0].timestamp} até {snapshots[-1].timestamp}")
    
    # Arquivar todos (pode demorar!)
    for i, snapshot in enumerate(snapshots, 1):
        print(f"\n[{i}/{len(snapshots)}] Arquivando: {snapshot.timestamp}")
        await archiver.archive_url(snapshot.url)
    
    print("\n✅ Histórico completo arquivado!")
    await archiver.shutdown()

asyncio.run(arquivar_historico())
```

### 8.2. Extrair Todos os Vídeos de Múltiplos Sites

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.config import load_config

async def extrair_videos():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    urls = [
        "https://web.archive.org/web/20090430060114/http://www.dar.org.br/",
        "https://web.archive.org/web/20050829171410fw_/http://www.ieabweb.org.br/",
    ]
    
    todos_videos = []
    
    for url in urls:
        snapshots = await archiver.discovery.find_snapshots(url)
        
        for snapshot in snapshots:
            downloaded = await archiver.ingestion.download(snapshot)
            if not downloaded:
                continue
            
            transformed = await archiver.transformation.transform(downloaded)
            if not transformed:
                continue
            
            # Analisar para encontrar embeds
            analysis = await archiver.intelligence.analyze(transformed)
            
            if analysis.media_embeds:
                print(f"\n🎥 {len(analysis.media_embeds)} vídeos em {snapshot.original_url}:")
                for embed in analysis.media_embeds:
                    print(f"  - {embed.platform}: {embed.url}")
                    todos_videos.append(embed)
    
    print(f"\n\n📊 TOTAL: {len(todos_videos)} vídeos encontrados")
    
    # Salvar lista de vídeos
    with open("videos_encontrados.txt", "w") as f:
        for video in todos_videos:
            f.write(f"{video.platform}\t{video.url}\n")
    
    print("✅ Lista salva em videos_encontrados.txt")
    
    await archiver.shutdown()

asyncio.run(extrair_videos())
```

### 8.3. Buscar e Exportar Resultados

```python
import asyncio
import json
from chronos_archiver.search import SearchEngine
from chronos_archiver.config import load_config

async def buscar_e_exportar():
    config = load_config()
    search = SearchEngine(config)
    
    # Buscar por termo
    termo = "diocese"
    resultados = await search.search(termo, limit=100)
    
    # Exportar para JSON
    dados_exportacao = []
    for r in resultados:
        dados_exportacao.append({
            "titulo": r.title,
            "url": r.url,
            "data": r.timestamp,
            "snippet": r.snippet,
            "score": r.score,
            "palavras_chave": r.keywords,
            "topicos": r.topics,
            "tem_videos": r.has_videos,
        })
    
    # Salvar JSON
    with open(f"busca_{termo}.json", "w", encoding="utf-8") as f:
        json.dump(dados_exportacao, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {len(resultados)} resultados exportados para busca_{termo}.json")

asyncio.run(buscar_e_exportar())
```

---

## Parte 9: Extração Avançada com Apache Tika

### 9.1. Extrair Texto de PDFs Arquivados

```python
import asyncio
from chronos_archiver.tika import TikaExtractor
from chronos_archiver.config import load_config

async def extrair_pdf():
    config = load_config()
    extractor = TikaExtractor(config)
    
    # Ler PDF arquivado
    with open("arquivo.pdf", "rb") as f:
        pdf_content = f.read()
    
    # Extrair com Tika
    result = extractor.extract_text(pdf_content)
    
    print("\n=== EXTRAÇÃO PDF ===")
    print(f"\nTexto Extraído ({len(result['text'])} caracteres):")
    print(result['text'][:500])  # Primeiros 500 chars
    
    print("\nMetadados:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")

asyncio.run(extrair_pdf())
```

---

## Parte 10: Monitoramento e Estatísticas

### 10.1. Estatísticas de Processamento

```python
import asyncio
from chronos_archiver import ChronosArchiver
from chronos_archiver.models import ProcessingStats
from chronos_archiver.config import load_config

async def monitorar():
    config = load_config()
    archiver = ChronosArchiver(config)
    
    # Carregar URLs
    with open("meus_sites.txt") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    # Inicializar estatísticas
    stats = ProcessingStats(total_snapshots=len(urls))
    
    # Processar com monitoramento
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        
        try:
            await archiver.archive_url(url)
            stats.indexed += 1
            print(f"  ✅ Sucesso")
        except Exception as e:
            stats.failed += 1
            print(f"  ❌ Erro: {e}")
    
    # Mostrar estatísticas finais
    stats.end_time = datetime.utcnow()
    
    print("\n" + "="*50)
    print("ESTATÍSTICAS FINAIS")
    print("="*50)
    print(f"Total: {stats.total_snapshots}")
    print(f"Sucesso: {stats.indexed}")
    print(f"Falhas: {stats.failed}")
    print(f"Taxa de Sucesso: {stats.success_rate:.1f}%")
    print(f"Tempo Total: {stats.duration:.1f}s")
    print("="*50)
    
    await archiver.shutdown()

asyncio.run(monitorar())
```

---

## Parte 11: Dicas Avançadas

### 11.1. Processar Apenas Páginas HTML

```yaml
# config.yaml
archive:
  allowed_mime_types:
    - "text/html"
```

### 11.2. Aumentar Performance

```yaml
processing:
  workers: 8                    # Mais workers
  concurrent_requests: 20       # Mais requests simultâneas
  batch_size: 20               # Lotes maiores
```

### 11.3. Habilitar Compressão

```yaml
indexing:
  compress_content: true
  compression_level: 9  # Máxima compressão
```

### 11.4. Usar PostgreSQL

```yaml
database:
  type: "postgresql"
  postgresql_url: "postgresql://chronos:senha@localhost:5432/chronos_db"
```

### 11.5. Configurar para Produção

```yaml
processing:
  workers: 16
  requests_per_second: 10
  retry_attempts: 5

database:
  type: "postgresql"
  pool_size: 20

logging:
  level: "INFO"
  log_to_file: true
  rotate_logs: true

api:
  host: "0.0.0.0"
  port: 8000
  enable_cors: true
```

---

## Parte 12: Troubleshooting Comum

### Problema: "Redis connection refused"

```bash
# Iniciar Redis
sudo systemctl start redis-server

# Ou com Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Problema: "Meilisearch not available"

```bash
# Verificar se está rodando
curl http://localhost:7700/health

# Iniciar Meilisearch
./meilisearch --http-addr 127.0.0.1:7700
```

### Problema: "spaCy model not found"

```bash
# Instalar modelo português
python -m spacy download pt_core_news_sm
```

### Problema: "Out of memory"

```yaml
# Reduzir uso de memória em config.yaml
processing:
  workers: 2
  concurrent_requests: 5
  batch_size: 5

archive:
  max_file_size: 50  # MB
```

---

## Recursos Adicionais

- 📚 [Documentação Completa](../README.md)
- 🧠 [Motor de Inteligência](INTELLIGENCE.md)
- 🔧 [Guia de Uso](usage.md)
- 🏛️ [Arquitetura](architecture.md)

---

**Sucesso no seu projeto de arquivamento! 🎉**

**Feito com ❤️ por Douglas Araujo**