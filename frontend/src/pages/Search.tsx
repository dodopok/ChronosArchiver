import { useState } from 'react'
import {
  Box,
  TextField,
  Button,
  Paper,
  Grid,
  Chip,
  Typography,
  InputAdornment,
  CircularProgress,
  Autocomplete,
} from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { searchContent, getSuggestions, getFacets } from '../services/api'
import { SearchFilters } from '../types'
import SearchResults from '../components/SearchResults'
import SearchFiltersPanel from '../components/SearchFiltersPanel'

export default function Search() {
  const [query, setQuery] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<SearchFilters>({})
  const [suggestions, setSuggestions] = useState<string[]>([])

  const { data: results, isLoading } = useQuery({
    queryKey: ['search', searchQuery, filters],
    queryFn: () => searchContent(searchQuery, filters),
    enabled: searchQuery.length > 0,
  })

  const { data: facets } = useQuery({
    queryKey: ['facets'],
    queryFn: getFacets,
  })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      setSearchQuery(query.trim())
    }
  }

  const handleInputChange = async (value: string) => {
    setQuery(value)
    if (value.length > 2) {
      const sugg = await getSuggestions(value)
      setSuggestions(sugg)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 700 }}>
        🔍 Busca Inteligente / Smart Search
      </Typography>

      {/* Search Bar */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleSearch}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={9}>
              <Autocomplete
                freeSolo
                options={suggestions}
                value={query}
                onInputChange={(_, value) => handleInputChange(value)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    placeholder="Pesquisar conteúdo arquivado..."
                    InputProps={{
                      ...params.InputProps,
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={isLoading}
                startIcon={isLoading ? <CircularProgress size={20} /> : <SearchIcon />}
              >
                {isLoading ? 'Buscando...' : 'Buscar'}
              </Button>
            </Grid>
          </Grid>
        </form>

        {/* Active Filters */}
        {(filters.topics || filters.has_videos) && (
          <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {filters.topics?.map((topic) => (
              <Chip
                key={topic}
                label={topic}
                onDelete={() =>
                  setFilters((prev) => ({
                    ...prev,
                    topics: prev.topics?.filter((t) => t !== topic),
                  }))
                }
              />
            ))}
            {filters.has_videos && (
              <Chip
                label="Has Videos"
                onDelete={() => setFilters((prev) => ({ ...prev, has_videos: undefined }))}
              />
            )}
          </Box>
        )}
      </Paper>

      <Grid container spacing={3}>
        {/* Filters Panel */}
        <Grid item xs={12} md={3}>
          <SearchFiltersPanel filters={filters} setFilters={setFilters} facets={facets} />
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={9}>
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {results && <SearchResults results={results.results} total={results.total} />}

          {searchQuery && !isLoading && results?.results.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">
                Nenhum resultado encontrado para "{searchQuery}"
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}