import { Box, Typography, Pagination } from '@mui/material'
import { SearchResult } from '../types'
import SearchResultCard from './SearchResultCard'
import { useState } from 'react'

interface SearchResultsProps {
  results: SearchResult[]
  total: number
}

export default function SearchResults({ results, total }: SearchResultsProps) {
  const [page, setPage] = useState(1)
  const resultsPerPage = 10

  const paginatedResults = results.slice(
    (page - 1) * resultsPerPage,
    page * resultsPerPage
  )

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {total} resultados encontrados / results found
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {paginatedResults.map((result) => (
          <SearchResultCard key={result.id} result={result} />
        ))}
      </Box>

      {total > resultsPerPage && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={Math.ceil(total / resultsPerPage)}
            page={page}
            onChange={(_, value) => setPage(value)}
            color="primary"
          />
        </Box>
      )}
    </Box>
  )
}