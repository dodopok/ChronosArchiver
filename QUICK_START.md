# 🚀 ChronosArchiver - Quick Start Guide
# 🚀 ChronosArchiver - Guia de Início Rápido

---

## ⏱️ 3 Minutos para Sistema Completo Rodando!
## ⏱️ 3 Minutes to Complete System Running!

---

## Passo 1: Clone o Repositório (10 segundos)

```bash
git clone https://github.com/dodopok/ChronosArchiver.git
cd ChronosArchiver
```

---

## Passo 2: Inicie TUDO com Docker (60 segundos)

```bash
docker-compose up -d
```

**Isso inicia automaticamente / This automatically starts:**

```
✅ Redis          (port 6379)  - Message queues
✅ Meilisearch    (port 7700)  - Search engine  
✅ Apache Tika    (port 9998)  - Text extraction
✅ PostgreSQL     (port 5432)  - Database
✅ FastAPI API    (port 8000)  - Backend + WebSocket
✅ React App      (port 3000)  - Web interface
✅ Workers (x2)              - Background processing
```

---

## Passo 3: Aguarde Inicialização (30 segundos)

```bash
# Verificar status
docker-compose ps

# Todos devem estar "Up" e "healthy"
```

Enquanto aguarda, veja os logs:
```bash
docker-compose logs -f api
```

---

## Passo 4: Acesse a Interface! (⚡ Instant)

### 🌐 Abra seu navegador em:

```
http://localhost:3000
```

Você verá / You'll see:

```
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│    🕒 ChronosArchiver                                          │
│                                                                  │
│    ┌──────────────────────────────────────────────────┐  │
│    │  📊 Dashboard  | 🔍 Search  | 📦 Archive  ...     │  │
│    └──────────────────────────────────────────────────┘  │
│                                                                  │
│    Interface moderna e responsiva / Modern responsive UI        │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Passo 5: Arquive Seu Primeiro Site! (⚡ Instant)

### Opção A: Via Interface Web

1. **Clique em "Archive"** na sidebar
2. **Cole uma URL** de exemplo:
   ```
   https://web.archive.org/web/20090430060114/http://www.dar.org.br/
   ```
3. **Clique "Add"** e depois **"Archive 1 URLs"**
4. **Volte para Dashboard** para ver progresso em tempo real!

### Opção B: Via CLI

```bash
chronos archive https://web.archive.org/web/20090430060114/http://www.dar.org.br/
```

### Opção C: Via API

```bash
curl -X POST http://localhost:8000/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://web.archive.org/web/20090430060114/http://www.dar.org.br/"],
    "priority": "normal"
  }'
```

---

## Passo 6: Monitore o Progresso! (⚡ Real-time)

No **Dashboard** você verá em tempo real:

```
┌────────────────────────────────────────────────────────────┐
│  🔍 Discovery    ████████████████████  100%  ✅          │
│  📥 Ingestion    ███████████████░░░░░   75%  ⏳          │
│  ♻️ Transform     ██████████░░░░░░░░░░   50%  ⏳          │
│  💾 Indexing     ░░░░░░░░░░░░░░░░░░░░    0%  ⏸️          │
└────────────────────────────────────────────────────────────┘
```

**Updates via WebSocket - sem refresh!**

---

## Passo 7: Busque o Conteúdo! (⚡ < 50ms)

1. **Vá para "Search"**
2. **Digite**: `diocese`
3. **Veja resultados instantâneos** com:
   - Título e URL
   - Snippet do conteúdo
   - Palavras-chave
   - Tópicos
   - Indicação de vídeos

4. **Use filtros**:
   - 🏷️ Tópicos (religião, notícias, etc.)
   - 🌎 Idiomas (pt, en, es)
   - 🎥 Has Videos
   - 🖼️ Has Images

---

## Passo 8: Explore Vídeos! (🎥)

1. **Vá para "Media Browser"**
2. **Veja galeria** de vídeos detectados
3. **Clique em um vídeo** para assistir
4. **Player embutido** abre automaticamente

```
┌────────────────────────────────────────────────────────────┐
│   [Thumbnail]    [Thumbnail]    [Thumbnail]    [Thumbnail]   │
│   YouTube        Vimeo          YouTube        Dailymotion   │
│   ▶️             ▶️             ▶️             ▶️            │
└────────────────────────────────────────────────────────────┘
```

---

## Passo 9: Veja Estatísticas! (📊)

1. **Vá para "Statistics"**
2. **Veja gráficos**:
   - 🧩 Pie chart de idiomas
   - 📊 Bar chart de tópicos  
   - 💳 Cards de estatísticas

---

## 🎉 Pronto! Sistema Completo Rodando!

### O que você tem agora / What you have now:

✅ **Interface web moderna** rodando em http://localhost:3000  
✅ **API REST completa** rodando em http://localhost:8000  
✅ **8 serviços integrados** rodando em containers  
✅ **WebSocket** para updates em tempo real  
✅ **Motor de inteligência** com NLP ativo  
✅ **Detecção de embeds** para YouTube/Vimeo  
✅ **Busca instantânea** com Meilisearch  
✅ **7 sites de exemplo** prontos para arquivar  

---

## 📚 Próximos Passos / Next Steps

### Arquivar Sites de Exemplo

```bash
# Via CLI
chronos archive --input examples/sample_sites.txt

# Via Interface Web
# 1. Vá para Archive
# 2. Drag & drop examples/sample_sites.txt
# 3. Clique "Archive 7 URLs"
```

### Explorar Recursos

1. 📊 **Dashboard** - Ver jobs em tempo real
2. 🔍 **Search** - Buscar conteúdo arquivado  
3. 🎥 **Media** - Navegar vídeos detectados
4. 📈 **Statistics** - Ver métricas e gráficos
5. ⚙️ **Settings** - Trocar tema dark/light

### Ler Documentação

- 🇧🇷 [Tutorial Português](docs/TUTORIAL_PT.md)
- 🇬🇧 [API Documentation](http://localhost:8000/api/docs)
- 📚 [Complete Docs](docs/)

---

## 🔧 Comandos Úteis / Useful Commands

```bash
# Ver logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f worker

# Reiniciar serviço
docker-compose restart api
docker-compose restart frontend

# Parar tudo
docker-compose down

# Reiniciar tudo
docker-compose down && docker-compose up -d

# Escalar workers
docker-compose up -d --scale worker=4
```

---

## 🆘 Troubleshooting Rápido / Quick Troubleshooting

### Frontend não carrega?

```bash
# Verificar status
docker-compose ps frontend

# Ver logs
docker-compose logs frontend

# Rebuild e restart
docker-compose build frontend
docker-compose up -d frontend
```

### Backend não responde?

```bash
# Health check
curl http://localhost:8000/health

# Ver logs
docker-compose logs api

# Restart
docker-compose restart api
```

### WebSocket não conecta?

```bash
# Verificar se API está rodando
curl http://localhost:8000/health

# Verificar logs do navegador (F12 -> Console)
# Deve ver: "WebSocket connected"
```

---

## 🎯 O Que Testar / What to Test

### 1. Dashboard
- [ ] Ver pipeline monitor
- [ ] Ver stat cards atualizando
- [ ] Ver recent jobs
- [ ] Receber notificações toast

### 2. Search  
- [ ] Buscar "diocese"
- [ ] Usar auto-complete
- [ ] Aplicar filtros
- [ ] Ver highlighting nos resultados

### 3. Archive
- [ ] Adicionar URL manualmente
- [ ] Upload arquivo .txt (drag & drop)
- [ ] Iniciar archiving
- [ ] Ver progresso em tempo real

### 4. Media Browser
- [ ] Ver galeria de vídeos
- [ ] Clicar em vídeo
- [ ] Assistir no player embutido

### 5. Statistics
- [ ] Ver charts de idioma
- [ ] Ver charts de tópicos
- [ ] Ver métricas gerais

### 6. Settings
- [ ] Trocar tema (dark/light)
- [ ] Ver informações do sistema

---

## 📚 Documentação Completa / Full Documentation

### Links Rápidos / Quick Links

- 🏠 [README Principal](README.md)
- 🚀 [Quick Start](QUICK_START.md) (este arquivo)
- 📖 [Tutorial PT](docs/TUTORIAL_PT.md)
- 📊 [Sistema Completo](COMPLETE_SYSTEM.md)
- 🌐 [Full-Stack Overview](FULL_STACK_OVERVIEW.md)
- 🔧 [Deploy Guide](DEPLOYMENT.md)
- 👨‍💻 [Contributing](CONTRIBUTING.md)

---

## ✨ Recursos Destacados / Highlighted Features

```
✅ Real-time WebSocket updates
✅ Auto-complete search  
✅ Drag & drop file upload
✅ Embedded video player
✅ Dark/Light theme
✅ Responsive mobile design
✅ Toast notifications
✅ Loading animations
✅ Error handling
✅ Bilingual UI (PT/EN)
✅ Intelligence analysis
✅ Media embed detection
✅ Advanced search filters
✅ Beautiful charts
✅ Professional design
```

---

## 🎓 Suporte / Support

- **GitHub Issues**: https://github.com/dodopok/ChronosArchiver/issues
- **Discussions**: https://github.com/dodopok/ChronosArchiver/discussions  
- **Email**: support@chronosarchiver.dev

---

**🎉 Parabéns! Você tem um sistema completo de arquivamento inteligente rodando! 🎉**

**🎉 Congratulations! You have a complete intelligent archiving system running! 🎉**

---

**Feito com ❤️ por Douglas Araujo**  
**Made with ❤️ by Douglas Araujo**