import { io, Socket } from 'socket.io-client'
import { ArchiveJob } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'http://localhost:8000'

let socket: Socket | null = null

export const connectWebSocket = (onJobUpdate: (job: ArchiveJob) => void): Socket => {
  if (socket) {
    return socket
  }

  socket = io(WS_URL, {
    path: '/ws/socket.io',
    transports: ['websocket'],
  })

  socket.on('connect', () => {
    console.log('WebSocket connected')
  })

  socket.on('job_update', (job: ArchiveJob) => {
    onJobUpdate(job)
  })

  socket.on('disconnect', () => {
    console.log('WebSocket disconnected')
  })

  socket.on('error', (error) => {
    console.error('WebSocket error:', error)
  })

  return socket
}

export const disconnectWebSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export const subscribeToJobs = () => {
  if (socket) {
    socket.emit('subscribe_jobs')
  }
}

export const unsubscribeFromJobs = () => {
  if (socket) {
    socket.emit('unsubscribe_jobs')
  }
}