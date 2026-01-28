import { Card, CardContent, Typography, Box } from '@mui/material'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning'
}

export default function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <Card
      sx={{
        height: '100%',
        background: (theme) =>
          `linear-gradient(135deg, ${theme.palette[color].main} 0%, ${theme.palette[color].dark} 100%)`,
        color: 'white',
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ opacity: 0.7 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  )
}