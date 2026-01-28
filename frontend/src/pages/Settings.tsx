import { Box, Typography, Paper, Switch, FormControlLabel, Divider } from '@mui/material'
import { useThemeStore } from '../store/useThemeStore'

export default function Settings() {
  const { mode, toggleTheme } = useThemeStore()

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        ⚙️ Configurações / Settings
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Preferências / Preferences
        </Typography>

        <FormControlLabel
          control={<Switch checked={mode === 'dark'} onChange={toggleTheme} />}
          label="Dark Mode"
        />

        <Divider sx={{ my: 3 }} />

        <Typography variant="h6" gutterBottom>
          Sobre / About
        </Typography>
        <Typography variant="body2" color="text.secondary">
          ChronosArchiver v1.1.0
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Sistema de arquivamento inteligente para a Wayback Machine
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Desenvolvido com ❤️ por Douglas Araujo
        </Typography>
      </Paper>
    </Box>
  )
}