import { Card, CardContent, Typography, Box, Chip, Button } from '@mui/material'
import { OpenInNew, VideoLibrary, CalendarToday } from '@mui/icons-material'
import { SearchResult } from '../types'
import { format } from 'date-fns'

interface SearchResultCardProps {
  result: SearchResult
}

export default function SearchResultCard({ result }: SearchResultCardProps) {
  const timestamp = result.timestamp
  const formattedDate = format(
    new Date(
      parseInt(timestamp.substring(0, 4)),
      parseInt(timestamp.substring(4, 6)) - 1,
      parseInt(timestamp.substring(6, 8))
    ),
    'PPP'
  )

  return (
    <Card sx={{ transition: 'all 0.3s', '&:hover': { boxShadow: 4 } }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
              {result.title || 'Untitled'}
            </Typography>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              {result.original_url}
            </Typography>

            <Typography variant="body2" sx={{ mb: 2 }}>
              {result.snippet}
            </Typography>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
              <Chip icon={<CalendarToday />} label={formattedDate} size="small" variant="outlined" />
              {result.has_videos && (
                <Chip icon={<VideoLibrary />} label="Has Videos" size="small" color="primary" />
              )}
              {result.topics.map((topic) => (
                <Chip key={topic} label={topic} size="small" />
              ))}
            </Box>

            {result.keywords.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Keywords: {result.keywords.slice(0, 5).join(', ')}
                </Typography>
              </Box>
            )}
          </Box>

          <Button
            variant="outlined"
            startIcon={<OpenInNew />}
            href={result.url}
            target="_blank"
            size="small"
          >
            View
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}