import { Dialog, DialogContent, DialogTitle, IconButton, Box } from '@mui/material'
import { Close } from '@mui/icons-material'
import ReactPlayer from 'react-player'
import { MediaEmbed } from '../types'

interface MediaPlayerProps {
  media: MediaEmbed
  onClose: () => void
}

export default function MediaPlayer({ media, onClose }: MediaPlayerProps) {
  return (
    <Dialog open onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {media.title || `${media.platform} Video`}
        <IconButton onClick={onClose}>
          <Close />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ position: 'relative', paddingTop: '56.25%' }}>
          <ReactPlayer
            url={media.embed_url}
            width="100%"
            height="100%"
            style={{ position: 'absolute', top: 0, left: 0 }}
            controls
          />
        </Box>
      </DialogContent>
    </Dialog>
  )
}