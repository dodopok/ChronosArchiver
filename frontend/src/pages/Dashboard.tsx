import { useEffect } from 'react'
import { Grid, Paper, Typography, Box, Card, CardContent, LinearProgress } from '@mui/material'
import {
  Archive as ArchiveIcon,
  CloudDownload,
  Transform,
  Storage,
} from '@mui/icons-material'
import { useJobStore } from '../store/useJobStore'
import { connectWebSocket, subscribeToJobs } from '../services/websocket'
import PipelineMonitor from '../components/PipelineMonitor'
import RecentJobs from '../components/RecentJobs'
import StatCard from '../components/StatCard'

export default function Dashboard() {
  const { jobs, updateJob } = useJobStore()

  useEffect(() => {
    const socket = connectWebSocket((job) => {
      updateJob(job.id, job)
    })

    subscribeToJobs()

    return () => {
      socket?.disconnect()
    }
  }, [])

  const activeJobs = jobs.filter((j) => !['indexed', 'failed', 'skipped'].includes(j.status))
  const completedJobs = jobs.filter((j) => j.status === 'indexed')
  const failedJobs = jobs.filter((j) => j.status === 'failed')

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        🚀 Dashboard de Arquivamento / Archiving Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Jobs"
            value={activeJobs.length}
            icon={<ArchiveIcon fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Completed"
            value={completedJobs.length}
            icon={<Storage fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Failed"
            value={failedJobs.length}
            icon={<Transform fontSize="large" />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total"
            value={jobs.length}
            icon={<CloudDownload fontSize="large" />}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Pipeline Monitor */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          📊 Pipeline Monitor
        </Typography>
        <PipelineMonitor jobs={activeJobs} />
      </Paper>

      {/* Recent Jobs */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          📋 Recent Jobs
        </Typography>
        <RecentJobs jobs={jobs.slice(0, 10)} />
      </Paper>
    </Box>
  )
}