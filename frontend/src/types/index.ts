export interface ArchiveSnapshot {
  url: string
  original_url: string
  timestamp: string
  mime_type?: string
  status_code?: number
  digest?: string
  length?: number
  status: ArchiveStatus
}

export enum ArchiveStatus {
  PENDING = 'pending',
  DISCOVERED = 'discovered',
  DOWNLOADING = 'downloading',
  DOWNLOADED = 'downloaded',
  TRANSFORMING = 'transforming',
  TRANSFORMED = 'transformed',
  ANALYZING = 'analyzing',
  ANALYZED = 'analyzed',
  INDEXING = 'indexing',
  INDEXED = 'indexed',
  FAILED = 'failed',
  SKIPPED = 'skipped',
}

export interface SearchResult {
  id: string
  url: string
  original_url: string
  timestamp: string
  title: string
  snippet: string
  highlights: Record<string, any>
  score: number
  keywords: string[]
  topics: string[]
  has_videos: boolean
  media_embeds: MediaEmbed[]
}

export interface MediaEmbed {
  type: string
  url: string
  embed_url: string
  video_id?: string
  platform: string
  title?: string
  thumbnail?: string
}

export interface SearchFilters {
  topics?: string[]
  languages?: string[]
  has_videos?: boolean
  has_images?: boolean
  date_from?: string
  date_to?: string
}

export interface ArchiveJob {
  id: string
  url: string
  status: ArchiveStatus
  progress: number
  stage: 'discovery' | 'ingestion' | 'transformation' | 'indexing'
  created_at: string
  updated_at: string
  error?: string
}

export interface Statistics {
  total_pages: number
  total_size: string
  oldest_snapshot: string
  newest_snapshot: string
  languages: Record<string, number>
  topics: Record<string, number>
  success_rate: number
  total_embeds: number
}

export interface ContentAnalysis {
  languages: [string, number][]
  entities: Record<string, string[]>
  keywords: string[]
  topics: string[]
  media_embeds: MediaEmbed[]
  summary?: string
  word_count: number
  has_images: boolean
  has_videos: boolean
}