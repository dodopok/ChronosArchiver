import { useState } from 'react'
import { Box, Typography, Grid, Tabs, Tab, Paper } from '@mui/material'
import { VideoLibrary, Image as ImageIcon, AudioFile } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { searchContent } from '../services/api'
import MediaCard from '../components/MediaCard'
import MediaPlayer from '../components/MediaPlayer'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  )
}

export default function MediaBrowser() {
  const [tab, setTab] = useState(0)
  const [selectedMedia, setSelectedMedia] = useState<any>(null)

  const { data: videoResults } = useQuery({
    queryKey: ['media', 'videos'],
    queryFn: () => searchContent('', { has_videos: true }, 50),
  })

  const videos = videoResults?.results.flatMap((r) => r.media_embeds) || []

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        🎥 Navegador de Mídia / Media Browser
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tab} onChange={(_, newValue) => setTab(newValue)}>
          <Tab icon={<VideoLibrary />} label="Vídeos" />
          <Tab icon={<ImageIcon />} label="Imagens" />
          <Tab icon={<AudioFile />} label="Áudio" />
        </Tabs>
      </Paper>

      <TabPanel value={tab} index={0}>
        <Grid container spacing={3}>
          {videos.map((embed, idx) => (
            <Grid item xs={12} sm={6} md={4} key={idx}>
              <MediaCard embed={embed} onClick={() => setSelectedMedia(embed)} />
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tab} index={1}>
        <Typography>Images coming soon...</Typography>
      </TabPanel>

      <TabPanel value={tab} index={2}>
        <Typography>Audio coming soon...</Typography>
      </TabPanel>

      {/* Media Player Modal */}
      {selectedMedia && (
        <MediaPlayer media={selectedMedia} onClose={() => setSelectedMedia(null)} />
      )}
    </Box>
  )
}