import { Routes, Route } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Search from './pages/Search'
import Archive from './pages/Archive'
import MediaBrowser from './pages/MediaBrowser'
import Statistics from './pages/Statistics'
import Settings from './pages/Settings'

function App() {
  return (
    <Layout>
      <Box sx={{ flexGrow: 1 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/search" element={<Search />} />
          <Route path="/archive" element={<Archive />} />
          <Route path="/media" element={<MediaBrowser />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Box>
    </Layout>
  )
}

export default App