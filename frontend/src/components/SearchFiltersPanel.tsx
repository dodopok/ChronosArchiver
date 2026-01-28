import {
  Paper,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Box,
  Chip,
} from '@mui/material'
import { SearchFilters } from '../types'

interface SearchFiltersPanelProps {
  filters: SearchFilters
  setFilters: (filters: SearchFilters) => void
  facets?: Record<string, Record<string, number>>
}

export default function SearchFiltersPanel({ filters, setFilters, facets }: SearchFiltersPanelProps) {
  const topics = facets?.topics || {}
  const languages = facets?.languages || {}

  const toggleTopic = (topic: string) => {
    const currentTopics = filters.topics || []
    const newTopics = currentTopics.includes(topic)
      ? currentTopics.filter((t) => t !== topic)
      : [...currentTopics, topic]
    setFilters({ ...filters, topics: newTopics.length > 0 ? newTopics : undefined })
  }

  return (
    <Paper sx={{ p: 2, position: 'sticky', top: 80 }}>
      <Typography variant="h6" gutterBottom>
        🔍 Filtros / Filters
      </Typography>

      <Divider sx={{ my: 2 }} />

      {/* Media Type */}
      <Typography variant="subtitle2" gutterBottom>
        Tipo de Mídia / Media Type
      </Typography>
      <FormGroup sx={{ mb: 2 }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={filters.has_videos || false}
              onChange={(e) => setFilters({ ...filters, has_videos: e.target.checked || undefined })}
            />
          }
          label="Has Videos"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={filters.has_images || false}
              onChange={(e) => setFilters({ ...filters, has_images: e.target.checked || undefined })}
            />
          }
          label="Has Images"
        />
      </FormGroup>

      <Divider sx={{ my: 2 }} />

      {/* Topics */}
      <Typography variant="subtitle2" gutterBottom>
        Tópicos / Topics
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
        {Object.entries(topics).map(([topic, count]) => (
          <Chip
            key={topic}
            label={`${topic} (${count})`}
            onClick={() => toggleTopic(topic)}
            color={filters.topics?.includes(topic) ? 'primary' : 'default'}
            variant={filters.topics?.includes(topic) ? 'filled' : 'outlined'}
          />
        ))}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Languages */}
      <Typography variant="subtitle2" gutterBottom>
        Idiomas / Languages
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {Object.entries(languages).map(([lang, count]) => (
          <Chip key={lang} label={`${lang} (${count})`} size="small" variant="outlined" />
        ))}
      </Box>
    </Paper>
  )
}