# ChronosArchiver React Frontend

## 🌐 Modern Web Interface for Intelligent Web Archiving

### Features

- ✅ **Real-time Monitoring Dashboard** - Live pipeline status with WebSocket updates
- ✅ **Smart Search Interface** - Auto-suggestions, filters, and faceted search
- ✅ **URL Management** - Add URLs manually or via file upload (drag & drop)
- ✅ **Media Browser** - Browse and play YouTube/Vimeo videos from archived sites
- ✅ **Statistics Dashboard** - Beautiful charts showing archive metrics
- ✅ **Dark/Light Theme** - Toggle between themes
- ✅ **Responsive Design** - Mobile-first, works on all devices
- ✅ **Bilingual UI** - Portuguese and English support

### Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Vite** for fast builds
- **React Query** for server state
- **Zustand** for client state
- **Socket.io** for WebSocket
- **Recharts** for visualizations
- **React Router** for navigation

## Quick Start

### Development

```bash
cd frontend
npm install
npm run dev
```

App will be available at: http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

### With Docker

```bash
# Build
docker build -t chronos-frontend .

# Run
docker run -p 3000:80 chronos-frontend
```

### With Docker Compose

```bash
# From root directory
docker-compose up -d frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── PipelineMonitor.tsx
│   │   ├── SearchResults.tsx
│   │   ├── SearchResultCard.tsx
│   │   ├── SearchFiltersPanel.tsx
│   │   ├── StatCard.tsx
│   │   ├── RecentJobs.tsx
│   │   ├── UrlList.tsx
│   │   ├── ArchiveJobProgress.tsx
│   │   ├── MediaCard.tsx
│   │   └── MediaPlayer.tsx
│   ├── pages/               # Application pages
│   │   ├── Dashboard.tsx
│   │   ├── Search.tsx
│   │   ├── Archive.tsx
│   │   ├── MediaBrowser.tsx
│   │   ├── Statistics.tsx
│   │   └── Settings.tsx
│   ├── services/            # API integration
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── store/               # State management
│   │   ├── useThemeStore.ts
│   │   └── useJobStore.ts
│   ├── hooks/               # Custom hooks
│   │   └── useWebSocket.ts
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── theme.ts             # MUI theme
│   ├── App.tsx              # Main app
│   └── main.tsx             # Entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── Dockerfile               # Docker build
└── nginx.conf               # Nginx config
```

## Components

### Dashboard
- Real-time job monitoring
- Pipeline visualization
- Recent jobs list
- Summary statistics

### Search
- Auto-complete search bar
- Advanced filters (topics, languages, media type)
- Paginated results
- Result highlighting

### Archive
- Manual URL entry
- Batch upload via drag & drop
- URL validation
- Active job progress tracking

### Media Browser
- Video, image, and audio tabs
- Grid view with thumbnails
- Embedded player for videos
- Platform-specific icons

### Statistics
- Archive overview cards
- Language distribution chart
- Topic distribution chart
- Timeline visualization

### Settings
- Theme toggle (dark/light)
- User preferences
- System information

## API Integration

### REST Endpoints

```typescript
// Search
GET /api/search?q=query&topics=topic1,topic2&limit=20

// Suggestions
GET /api/suggest?q=partial

// Facets
GET /api/facets

// Statistics
GET /api/stats

// Archive URLs
POST /api/archive
{
  "urls": ["url1", "url2"],
  "priority": "normal"
}

// Get Jobs
GET /api/jobs

// Health Check
GET /health
```

### WebSocket

```typescript
// Connect
const socket = io('http://localhost:8000')

// Listen for job updates
socket.on('job_update', (job) => {
  console.log('Job updated:', job)
})
```

## Development

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

### Running Locally

```bash
# Terminal 1: Start backend
cd ..
docker-compose up -d api redis meilisearch tika

# Terminal 2: Start frontend
cd frontend
npm install
npm run dev
```

### Testing

```bash
npm test
npm run test:coverage
```

### Linting

```bash
npm run lint
```

## Deployment

### Production Build

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Frontend will be available at http://localhost:3000
# API at http://localhost:8000
```

## Features in Detail

### Real-time Updates

The dashboard connects to the backend via WebSocket and receives live updates:

```typescript
// Automatic updates when jobs progress
Discovery -> Ingestion -> Transformation -> Indexing
     25%        50%            75%            100%
```

### Search Features

- **Auto-suggestions**: As you type
- **Typo tolerance**: Finds results even with spelling mistakes
- **Faceted filtering**: Filter by topic, language, media type
- **Highlighting**: Search terms highlighted in results
- **Pagination**: Navigate through large result sets

### Archive Features

- **Single URL**: Add one URL at a time
- **Batch upload**: Drag & drop .txt or .csv files
- **Progress tracking**: See real-time progress for each URL
- **Error handling**: Clear error messages with retry options

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Made with ❤️ by Douglas Araujo**