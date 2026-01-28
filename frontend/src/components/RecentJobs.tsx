import {
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  LinearProgress,
  Typography,
} from '@mui/material'
import { ArchiveJob, ArchiveStatus } from '../types'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface RecentJobsProps {
  jobs: ArchiveJob[]
}

const statusColors: Record<ArchiveStatus, any> = {
  [ArchiveStatus.PENDING]: 'default',
  [ArchiveStatus.DISCOVERED]: 'info',
  [ArchiveStatus.DOWNLOADING]: 'primary',
  [ArchiveStatus.DOWNLOADED]: 'primary',
  [ArchiveStatus.TRANSFORMING]: 'secondary',
  [ArchiveStatus.TRANSFORMED]: 'secondary',
  [ArchiveStatus.ANALYZING]: 'secondary',
  [ArchiveStatus.ANALYZED]: 'secondary',
  [ArchiveStatus.INDEXING]: 'success',
  [ArchiveStatus.INDEXED]: 'success',
  [ArchiveStatus.FAILED]: 'error',
  [ArchiveStatus.SKIPPED]: 'warning',
}

export default function RecentJobs({ jobs }: RecentJobsProps) {
  if (jobs.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
        No recent jobs
      </Typography>
    )
  }

  return (
    <List>
      {jobs.map((job) => (
        <ListItem
          key={job.id}
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
            mb: 1,
          }}
        >
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 600, flexGrow: 1 }}>
                  {job.url}
                </Typography>
                <Chip label={job.status} size="small" color={statusColors[job.status]} />
              </Box>
            }
            secondary={
              <Box>
                <Typography variant="caption" color="text.secondary">
                  {formatDistanceToNow(new Date(job.created_at), { addSuffix: true, locale: ptBR })}
                </Typography>
                {job.progress < 100 && job.status !== ArchiveStatus.FAILED && (
                  <LinearProgress
                    variant="determinate"
                    value={job.progress}
                    sx={{ mt: 1, height: 4, borderRadius: 2 }}
                  />
                )}
                {job.error && (
                  <Typography variant="caption" color="error" sx={{ display: 'block', mt: 1 }}>
                    Error: {job.error}
                  </Typography>
                )}
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  )
}