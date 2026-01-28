import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Grid,
  Alert,
  Chip,
  IconButton,
} from '@mui/material'
import { Archive as ArchiveIcon, Add, Delete, Upload } from '@mui/icons-material'
import { useDropzone } from 'react-dropzone'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { archiveUrls } from '../services/api'
import { useJobStore } from '../store/useJobStore'
import UrlList from '../components/UrlList'
import ArchiveJobProgress from '../components/ArchiveJobProgress'

export default function Archive() {
  const [urls, setUrls] = useState<string[]>([])
  const [currentUrl, setCurrentUrl] = useState('')
  const { jobs } = useJobStore()

  const archiveMutation = useMutation({
    mutationFn: (urlList: string[]) => archiveUrls(urlList),
    onSuccess: () => {
      toast.success(`Started archiving ${urls.length} URLs`)
      setUrls([])
    },
    onError: (error) => {
      toast.error(`Failed to start archiving: ${error}`)
    },
  })

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'text/csv': ['.csv'],
    },
    onDrop: (acceptedFiles) => {
      acceptedFiles.forEach((file) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const text = e.target?.result as string
          const lines = text
            .split('\n')
            .map((line) => line.trim())
            .filter((line) => line && !line.startsWith('#'))
          setUrls((prev) => [...prev, ...lines])
          toast.success(`Loaded ${lines.length} URLs from ${file.name}`)
        }
        reader.readAsText(file)
      })
    },
  })

  const addUrl = () => {
    if (currentUrl.trim() && !urls.includes(currentUrl.trim())) {
      setUrls([...urls, currentUrl.trim()])
      setCurrentUrl('')
    }
  }

  const removeUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index))
  }

  const startArchiving = () => {
    if (urls.length > 0) {
      archiveMutation.mutate(urls)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        📦 Arquivar URLs / Archive URLs
      </Typography>

      <Grid container spacing={3}>
        {/* URL Input */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Adicionar URLs / Add URLs
            </Typography>

            {/* Manual Entry */}
            <Box sx={{ mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs>
                  <TextField
                    fullWidth
                    placeholder="https://web.archive.org/web/20090430060114/http://www.dar.org.br/"
                    value={currentUrl}
                    onChange={(e) => setCurrentUrl(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && addUrl()}
                  />
                </Grid>
                <Grid item>
                  <Button variant="contained" onClick={addUrl} startIcon={<Add />}>
                    Add
                  </Button>
                </Grid>
              </Grid>
            </Box>

            {/* File Upload */}
            <Paper
              {...getRootProps()}
              sx={{
                p: 3,
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'divider',
                bgcolor: isDragActive ? 'action.hover' : 'background.default',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.3s',
              }}
            >
              <input {...getInputProps()} />
              <Upload sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="body1" gutterBottom>
                {isDragActive ? 'Solte o arquivo aqui' : 'Arraste um arquivo .txt ou .csv'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ou clique para selecionar
              </Typography>
            </Paper>

            {/* URL List */}
            {urls.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  URLs para arquivar ({urls.length}):
                </Typography>
                <UrlList urls={urls} onRemove={removeUrl} />
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={startArchiving}
                  disabled={archiveMutation.isPending}
                  startIcon={<ArchiveIcon />}
                  sx={{ mt: 2 }}
                >
                  {archiveMutation.isPending ? 'Starting...' : `Archive ${urls.length} URLs`}
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Active Jobs */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              ⏳ Trabalhos Ativos / Active Jobs
            </Typography>

            {activeJobs.length === 0 ? (
              <Alert severity="info">Nenhum trabalho em andamento / No active jobs</Alert>
            ) : (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {activeJobs.map((job) => (
                  <ArchiveJobProgress key={job.id} job={job} />
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}