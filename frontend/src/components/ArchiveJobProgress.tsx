import { Paper, Box, Typography, LinearProgress, Chip } from '@mui/material'
import { ArchiveJob } from '../types'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface ArchiveJobProgressProps {
  job: ArchiveJob
}

const stageLabels = {
  discovery: 'Discovering',
  ingestion: 'Downloading',
  transformation: 'Transforming',
  indexing: 'Indexing',
}

export default function ArchiveJobProgress({ job }: ArchiveJobProgressProps) {
  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, gap: 1 }}>
        <Typography variant="body2" sx={{ flexGrow: 1, fontWeight: 600 }} noWrap>
          {job.url}
        </Typography>
        <Chip label={stageLabels[job.stage]} size="small" color="primary" />
      </Box>

      <LinearProgress variant="determinate" value={job.progress} sx={{ mb: 1, height: 8, borderRadius: 4 }} />

      <Typography variant="caption" color="text.secondary">
        {formatDistanceToNow(new Date(job.created_at), { addSuffix: true, locale: ptBR })} • {job.progress}%
      </Typography>
    </Paper>
  )
}