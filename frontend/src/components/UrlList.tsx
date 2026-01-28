import { List, ListItem, ListItemText, IconButton, Box, Typography } from '@mui/material'
import { Delete } from '@mui/icons-material'

interface UrlListProps {
  urls: string[]
  onRemove: (index: number) => void
}

export default function UrlList({ urls, onRemove }: UrlListProps) {
  return (
    <List
      sx={{
        maxHeight: 300,
        overflow: 'auto',
        border: 1,
        borderColor: 'divider',
        borderRadius: 2,
      }}
    >
      {urls.map((url, index) => (
        <ListItem
          key={index}
          secondaryAction={
            <IconButton edge="end" onClick={() => onRemove(index)}>
              <Delete />
            </IconButton>
          }
        >
          <ListItemText
            primary={
              <Typography variant="body2" noWrap>
                {url}
              </Typography>
            }
          />
        </ListItem>
      ))}
    </List>
  )
}