import axios from 'axios'
import type { Project, RoiConfig, ScreenshotItem } from '../types'

export const api = axios.create({
  baseURL: '',
})

function unwrapError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail ?? error.response?.data
    return detail?.message ?? detail?.code ?? error.message
  }
  return error instanceof Error ? error.message : '请求失败'
}

export async function createProject(name: string): Promise<string> {
  try {
    const response = await api.post('/api/projects', { name })
    return response.data.project_id
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function fetchProject(projectId: string): Promise<Project> {
  try {
    const response = await api.get(`/api/projects/${projectId}`)
    return response.data
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function uploadImages(projectId: string, files: File[]): Promise<ScreenshotItem[]> {
  try {
    const form = new FormData()
    files.forEach((file) => form.append('files', file))
    const response = await api.post(`/api/projects/${projectId}/images`, form)
    return response.data.items
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function updateRoi(projectId: string, roi: RoiConfig): Promise<void> {
  try {
    await api.put(`/api/projects/${projectId}/roi`, roi)
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function generateStrips(projectId: string): Promise<ScreenshotItem[]> {
  try {
    const response = await api.post(`/api/projects/${projectId}/strips`)
    return response.data.items
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function updateImage(
  projectId: string,
  imageId: string,
  payload: Partial<Pick<ScreenshotItem, 'selected' | 'is_cover' | 'order'>>,
): Promise<ScreenshotItem> {
  try {
    const response = await api.put(`/api/projects/${projectId}/images/${imageId}`, payload)
    return response.data
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function deleteImage(projectId: string, imageId: string): Promise<void> {
  try {
    await api.delete(`/api/projects/${projectId}/images/${imageId}`)
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function reorderImages(projectId: string, imageIds: string[]): Promise<ScreenshotItem[]> {
  try {
    const response = await api.put(`/api/projects/${projectId}/images/order`, { image_ids: imageIds })
    return response.data.items
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}

export async function exportCollage(
  projectId: string,
  payload: { format: string; gap: number; background: string },
): Promise<string> {
  try {
    const response = await api.post(`/api/projects/${projectId}/export`, payload)
    return response.data.download_url
  } catch (error) {
    throw new Error(unwrapError(error))
  }
}
