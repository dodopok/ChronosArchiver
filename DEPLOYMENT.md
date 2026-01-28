# 🚀 Guia de Deploy / Deployment Guide

## ChronosArchiver - Sistema Completo Full-Stack

---

## 💻 Desenvolvimento Local / Local Development

### Método 1: Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# 2. Copie o arquivo de configuração
cp config.yaml.example config.yaml

# 3. Inicie todos os serviços
docker-compose up -d

# 4. Aguarde os serviços iniciarem (~30 segundos)
sleep 30

# 5. Verifique os serviços
docker-compose ps

# 6. Veja os logs
docker-compose logs -f api
docker-compose logs -f frontend
```

**Serviços disponíveis:**
- 🌐 Frontend React: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/api/docs
- 🔍 Meilisearch: http://localhost:7700
- 📊 Redis: localhost:6379
- 📑 Tika: http://localhost:9998
- 📦 PostgreSQL: localhost:5432

### Método 2: Manual (Desenvolvimento)

#### Terminal 1: Backend

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install -e .

# Instalar modelos NLP
python -m spacy download pt_core_news_sm
python -m spacy download xx_ent_wiki_sm

# Iniciar Redis
redis-server &

# Iniciar Meilisearch
meilisearch --http-addr 127.0.0.1:7700 &

# Iniciar Tika (Docker)
docker run -d -p 9998:9998 apache/tika:latest

# Iniciar API
uvicorn chronos_archiver.api:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2: Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar dev server
npm run dev
```

#### Terminal 3: Workers

```bash
source venv/bin/activate
chronos workers start --count 4
```

---

## 🏭 Produção / Production Deployment

### Pré-requisitos

- **Servidor** com Docker e Docker Compose
- **Domínio** (opcional, para HTTPS)
- **4GB RAM** mínimo (8GB recomendado)
- **20GB disco** mínimo (mais para arquivos)

### Passo 1: Preparar Servidor

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose git

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

### Passo 2: Clonar e Configurar

```bash
# Clone
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver

# Configure
cp config.yaml.example config.yaml
nano config.yaml
```

**Ajustar para produção:**

```yaml
processing:
  workers: 8                    # Aumentar workers
  requests_per_second: 10       # Aumentar rate

database:
  type: "postgresql"
  postgresql_url: "postgresql://chronos:senha_segura@postgres:5432/chronos"

logging:
  level: "INFO"
  log_to_file: true

api:
  host: "0.0.0.0"
  port: 8000
  enable_cors: true
  cors_origins:
    - "https://seu-dominio.com"
    - "http://localhost:3000"
```

### Passo 3: Configurar Variáveis de Ambiente

Crie `.env` na raiz:

```env
# PostgreSQL
POSTGRES_PASSWORD=senha_segura_aqui

# Meilisearch (opcional)
MEILI_MASTER_KEY=chave_master_segura

# Frontend
VITE_API_URL=https://api.seu-dominio.com
VITE_WS_URL=wss://api.seu-dominio.com
```

### Passo 4: Build e Deploy

```bash
# Build imagens
docker-compose build

# Iniciar em modo produção
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Passo 5: Configurar Nginx Reverse Proxy (Opcional)

Para HTTPS com Let's Encrypt:

```nginx
# /etc/nginx/sites-available/chronos
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

---

## 🔄 Atualização / Updates

```bash
# Parar serviços
docker-compose down

# Atualizar código
git pull origin main

# Rebuild se necessário
docker-compose build

# Reiniciar
docker-compose up -d
```

---

## 📊 Monitoramento / Monitoring

### Health Checks

```bash
# API
curl http://localhost:8000/health

# Meilisearch
curl http://localhost:7700/health

# Redis
redis-cli ping
```

### Logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f worker
```

### Métricas

```bash
# Ver estatísticas de container
docker stats

# Ver uso de disco
du -sh archive/

# Ver tamanho do banco
du -sh archive/chronos.db
```

---

## 🔧 Manutenção / Maintenance

### Backup

```bash
# Backup do arquivo
tar -czf archive_backup_$(date +%Y%m%d).tar.gz archive/

# Backup do banco PostgreSQL
docker-compose exec postgres pg_dump -U chronos chronos > backup.sql

# Backup do índice Meilisearch
curl -X POST http://localhost:7700/dumps
```

### Limpeza

```bash
# Limpar jobs antigos
docker-compose exec api python -c "from chronos_archiver.api import active_jobs; active_jobs.clear()"

# Limpar logs antigos
find logs/ -name "*.log" -mtime +30 -delete

# Limpar volumes não usados
docker volume prune
```

### Escalar Workers

```bash
# Aumentar número de workers
docker-compose up -d --scale worker=4

# Reduzir
docker-compose up -d --scale worker=1
```

---

## 🔐 Segurança / Security

### Produção Checklist

- [ ] Alterar senhas padrão do PostgreSQL
- [ ] Configurar Meilisearch API key
- [ ] Habilitar HTTPS
- [ ] Configurar CORS apropriadamente
- [ ] Limitar acesso aos portos (firewall)
- [ ] Configurar backup automático
- [ ] Monitorar logs de segurança
- [ ] Atualizar dependências regularmente

### Firewall

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

---

## ⚡ Performance / Otimização

### Para Alta Performance

```yaml
# config.yaml
processing:
  workers: 16
  concurrent_requests: 30
  batch_size: 50

database:
  type: "postgresql"
  pool_size: 20
  max_overflow: 30

indexing:
  compress_content: true
  compression_level: 6
```

### Recursos de Servidor Recomendados

| Carga | CPU | RAM | Disco | Workers |
|-------|-----|-----|-------|--------|
| Pequena | 2 cores | 4GB | 50GB | 2-4 |
| Média | 4 cores | 8GB | 200GB | 4-8 |
| Grande | 8+ cores | 16GB+ | 500GB+ | 8-16 |

---

## 🆘 Troubleshooting

### Frontend não carrega

```bash
# Verificar se o container está rodando
docker-compose ps frontend

# Ver logs
docker-compose logs frontend

# Rebuild
docker-compose build frontend
docker-compose up -d frontend
```

### WebSocket não conecta

```bash
# Verificar se API está acessível
curl http://localhost:8000/health

# Verificar configuração CORS
# Editar src/chronos_archiver/api.py
```

### Meilisearch não indexa

```bash
# Verificar conexão
curl http://localhost:7700/health

# Ver logs
docker-compose logs meilisearch

# Reiniciar
docker-compose restart meilisearch
```

---

## 📦 Ambientes / Environments

### Desenvolvimento / Development

```bash
docker-compose up -d
```

### Staging

```bash
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### Produção / Production

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📊 Monitoramento Contínuo / Continuous Monitoring

### Com Prometheus (Futuro)

```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Com Grafana (Futuro)

```yaml
grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## ✅ Checklist de Deploy

### Antes do Deploy

- [ ] Testes passando (backend e frontend)
- [ ] Configuração revisada
- [ ] Variáveis de ambiente configuradas
- [ ] Senhas alteradas
- [ ] Backup configurado
- [ ] Monitoramento configurado

### Após Deploy

- [ ] Health checks passando
- [ ] Frontend acessível
- [ ] API respondendo
- [ ] WebSocket funcionando
- [ ] Busca funcionando
- [ ] Workers processando
- [ ] Logs sem erros

---

**Sucesso no seu deploy! 🎉**