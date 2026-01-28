import { create } from 'zustand'
import { ArchiveJob } from '../types'

interface JobState {
  jobs: ArchiveJob[]
  addJob: (job: ArchiveJob) => void
  updateJob: (jobId: string, updates: Partial<ArchiveJob>) => void
  clearJobs: () => void
}

export const useJobStore = create<JobState>((set) => ({
  jobs: [],
  addJob: (job) => set((state) => ({ jobs: [job, ...state.jobs] })),
  updateJob: (jobId, updates) =>
    set((state) => ({
      jobs: state.jobs.map((job) => (job.id === jobId ? { ...job, ...updates } : job)),
    })),
  clearJobs: () => set({ jobs: [] }),
}))