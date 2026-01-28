import axios from 'axios'
import { SearchResult, SearchFilters, Statistics, ArchiveJob } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Search
export const searchContent = async (
  query: string,
  filters?: SearchFilters,
  limit: number = 20,
  offset: number = 0
): Promise<{ results: SearchResult[]; total: number }> => {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    offset: offset.toString(),
  })

  if (filters?.topics) params.append('topics', filters.topics.join(','))
  if (filters?.has_videos !== undefined) params.append('has_videos', filters.has_videos.toString())

  const response = await api.get(`/api/search?${params}`)
  return response.data
}

// Suggestions
export const getSuggestions = async (query: string): Promise<string[]> => {
  const response = await api.get(`/api/suggest?q=${encodeURIComponent(query)}`)
  return response.data.suggestions
}

// Facets
export const getFacets = async (): Promise<Record<string, Record<string, number>>> => {
  const response = await api.get('/api/facets')
  return response.data
}

// Statistics
export const getStatistics = async (): Promise<Statistics> => {
  const response = await api.get('/api/stats')
  return response.data
}

// Archive URL
export const archiveUrl = async (url: string, priority: string = 'normal'): Promise<{ job_id: string }> => {
  const response = await api.post('/api/archive', { urls: [url], priority })
  return response.data
}

// Archive multiple URLs
export const archiveUrls = async (urls: string[], priority: string = 'normal'): Promise<{ job_ids: string[] }> => {
  const response = await api.post('/api/archive', { urls, priority })
  return response.data
}

// Get archive jobs
export const getArchiveJobs = async (): Promise<ArchiveJob[]> => {
  const response = await api.get('/api/jobs')
  return response.data
}

// Health check
export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/health')
  return response.data
}