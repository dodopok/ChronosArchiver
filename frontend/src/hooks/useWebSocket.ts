import { useEffect } from 'react'
import { connectWebSocket, disconnectWebSocket, subscribeToJobs } from '../services/websocket'
import { useJobStore } from '../store/useJobStore'

export const useWebSocket = () => {
  const { updateJob, addJob } = useJobStore()

  useEffect(() => {
    const socket = connectWebSocket((job) => {
      // Update or add job
      updateJob(job.id, job)
    })

    subscribeToJobs()

    return () => {
      disconnectWebSocket()
    }
  }, [updateJob, addJob])
}