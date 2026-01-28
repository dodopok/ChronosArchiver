import { Card, CardMedia, CardContent, Typography, Box, Chip } from '@mui/material'
import { PlayCircle } from '@mui/icons-material'
import { MediaEmbed } from '../types'

interface MediaCardProps {
  embed: MediaEmbed
  onClick: () => void
}

const getThumbnail = (embed: MediaEmbed): string => {
  if (embed.thumbnail) return embed.thumbnail

  if (embed.type === 'youtube' && embed.video_id) {
    return `https://img.youtube.com/vi/${embed.video_id}/mqdefault.jpg`
  }

  if (embed.type === 'vimeo' && embed.video_id) {
    return `https://vumbnail.com/${embed.video_id}.jpg`
  }

  return 'https://via.placeholder.com/320x180?text=Video'
}

export default function MediaCard({ embed, onClick }: MediaCardProps) {
  return (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.3s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={onClick}
    >
      <Box sx={{ position: 'relative' }}>
        <CardMedia component="img" height="180" image={getThumbnail(embed)} alt={embed.title || 'Video'} />
        <PlayCircle
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            fontSize: 64,
            color: 'white',
            opacity: 0.9,
          }}
        />
      </Box>
      <CardContent>
        <Typography variant="body2" gutterBottom noWrap>
          {embed.title || embed.platform}
        </Typography>
        <Chip label={embed.platform} size="small" color="primary" />
      </CardContent>
    </Card>
  )
}