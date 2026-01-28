import { Box, Typography, Grid, Paper } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getStatistics } from '../services/api'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import StatCard from '../components/StatCard'
import { Storage, Language, Topic, VideoLibrary } from '@mui/icons-material'

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']

export default function Statistics() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['statistics'],
    queryFn: getStatistics,
  })

  if (isLoading || !stats) {
    return <Typography>Loading statistics...</Typography>
  }

  const languageData = Object.entries(stats.languages || {}).map(([name, value]) => ({
    name,
    value,
  }))

  const topicData = Object.entries(stats.topics || {}).map(([name, value]) => ({
    name,
    value,
  }))

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        📊 Estatísticas / Statistics
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Pages"
            value={stats.total_pages}
            icon={<Storage fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Size"
            value={stats.total_size}
            icon={<Storage fontSize="large" />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${stats.success_rate}%`}
            icon={<Storage fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Media Embeds"
            value={stats.total_embeds}
            icon={<VideoLibrary fontSize="large" />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Language Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🌎 Distribuição de Idiomas / Language Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={languageData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {languageData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Topic Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🏷️ Distribuição de Tópicos / Topic Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={topicData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}