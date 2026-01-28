import { Box, Paper, Typography, LinearProgress, Chip } from '@mui/material'
import { ArchiveJob, ArchiveStatus } from '../types'
import { CloudDownload, Transform, Storage, CheckCircle } from '@mui/icons-material'

interface PipelineMonitorProps {
  jobs: ArchiveJob[]
}

const stageIcons = {
  discovery: <CloudDownload />,
  ingestion: <CloudDownload />,
  transformation: <Transform />,
  indexing: <Storage />,
}

const getStageProgress = (jobs: ArchiveJob[], stage: string): number => {
  const stageJobs = jobs.filter((j) => j.stage === stage)
  if (stageJobs.length === 0) return 0
  return stageJobs.reduce((sum, job) => sum + job.progress, 0) / stageJobs.length
}

export default function PipelineMonitor({ jobs }: PipelineMonitorProps) {
  const stages = ['discovery', 'ingestion', 'transformation', 'indexing']

  if (jobs.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="text.secondary">No active jobs</Typography>
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', gap: 2, flexDirection: 'column' }}>
      {stages.map((stage) => {
        const progress = getStageProgress(jobs, stage)
        const activeJobs = jobs.filter((j) => j.stage === stage).length

        return (
          <Box key={stage}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, gap: 1 }}>
              {stageIcons[stage as keyof typeof stageIcons]}
              <Typography variant="subtitle2" sx={{ textTransform: 'capitalize', flexGrow: 1 }}>
                {stage}
              </Typography>
              <Chip label={`${activeJobs} active`} size="small" color="primary" />
            </Box>
            <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
          </Box>
        )
      })}
    </Box>
  )
}