import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Project, RoiConfig, ScreenshotItem } from '../types'
import {
  createProject,
  deleteImage,
  exportCollage,
  fetchProject,
  generateStrips,
  reorderImages,
  updateImage,
  updateRoi,
  uploadImages,
} from '../api/client'

export const useProjectStore = defineStore('project', () => {
  const projectStorageKey = 'subtitle-collage-project-id'
  const project = ref<Project | null>(null)
  const currentId = ref<string>('')
  const loading = ref(false)
  const exportUrl = ref('')
  const roiError = ref('')
  const localUrls = new Map<string, string>()
  let roiSaveTimer: ReturnType<typeof window.setTimeout> | undefined

  const screenshots = computed(() => [...(project.value?.screenshots ?? [])].sort((a, b) => a.order - b.order))
  const current = computed(() => screenshots.value.find((item) => item.id === currentId.value) ?? screenshots.value[0])

  function withUrls(source: Project): Project {
    const height = source.roi ? Math.min(0.8, Math.max(0.03, source.roi.height)) : undefined
    return {
      ...source,
      roi: height ? { x: 0, y: 1 - height, width: 1, height } : undefined,
      screenshots: source.screenshots.map((item) => ({
        ...item,
        local_url: localUrls.get(item.id),
        original_url: `/api/files/${source.id}/${item.original_path}`,
        preview_url: item.preview_path ? `/api/files/${source.id}/${item.preview_path}` : undefined,
        cropped_url: item.cropped_path ? `/api/files/${source.id}/${item.cropped_path}` : undefined,
      })),
    }
  }

  async function ensureProject() {
    if (project.value) return
    loading.value = true
    try {
      const savedProjectId = window.localStorage.getItem(projectStorageKey)
      if (savedProjectId) {
        try {
          project.value = withUrls(await fetchProject(savedProjectId))
          currentId.value = project.value.screenshots[0]?.id || ''
          return
        } catch {
          window.localStorage.removeItem(projectStorageKey)
        }
      }
      const projectId = await createProject('Subtitle Collage')
      window.localStorage.setItem(projectStorageKey, projectId)
      project.value = withUrls(await fetchProject(projectId))
    } finally {
      loading.value = false
    }
  }

  async function addFiles(files: File[]) {
    await ensureProject()
    if (!project.value || files.length === 0) return
    loading.value = true
    try {
      const uploaded = await uploadImages(project.value.id, files)
      uploaded.forEach((item, index) => {
        const file = files[index]
        if (file) localUrls.set(item.id, URL.createObjectURL(file))
      })
      project.value = withUrls(await fetchProject(project.value.id))
      const firstNewIndex = Math.max(0, project.value.screenshots.length - files.length)
      currentId.value = project.value.screenshots[firstNewIndex]?.id || project.value.screenshots[0]?.id || ''
    } finally {
      loading.value = false
    }
  }

  async function saveRoi(roi: RoiConfig) {
    if (!project.value) return
    project.value.roi = roi
    roiError.value = ''
    if (roiSaveTimer) window.clearTimeout(roiSaveTimer)
    const projectId = project.value.id
    roiSaveTimer = window.setTimeout(() => {
      updateRoi(projectId, roi).catch((error) => {
        roiError.value = error instanceof Error ? error.message : '字幕高度保存失败'
      })
    }, 220)
  }

  async function refreshStrips() {
    if (!project.value) return
    loading.value = true
    try {
      project.value.screenshots = generateUrls(await generateStrips(project.value.id), project.value.id)
    } finally {
      loading.value = false
    }
  }

  function generateUrls(items: ScreenshotItem[], projectId: string): ScreenshotItem[] {
    return items.map((item) => ({
      ...item,
      local_url: localUrls.get(item.id),
      original_url: `/api/files/${projectId}/${item.original_path}`,
      preview_url: item.preview_path ? `/api/files/${projectId}/${item.preview_path}` : undefined,
      cropped_url: item.cropped_path ? `/api/files/${projectId}/${item.cropped_path}` : undefined,
    }))
  }

  async function patchImage(imageId: string, payload: Parameters<typeof updateImage>[2]) {
    if (!project.value) return
    const updated = await updateImage(project.value.id, imageId, payload)
    const index = project.value.screenshots.findIndex((item) => item.id === imageId)
    if (index >= 0) project.value.screenshots[index] = { ...project.value.screenshots[index], ...updated }
    if (payload.is_cover) {
      project.value.screenshots.forEach((item) => {
        item.is_cover = item.id === imageId
      })
    }
  }

  async function removeImage(imageId: string) {
    if (!project.value) return
    await deleteImage(project.value.id, imageId)
    const localUrl = localUrls.get(imageId)
    if (localUrl) URL.revokeObjectURL(localUrl)
    localUrls.delete(imageId)
    project.value = withUrls(await fetchProject(project.value.id))
    if (currentId.value === imageId) currentId.value = project.value.screenshots[0]?.id || ''
  }

  async function saveOrder(items: ScreenshotItem[]) {
    if (!project.value) return
    project.value.screenshots = items.map((item, index) => ({ ...item, order: index + 1 }))
    project.value.screenshots = await reorderImages(
      project.value.id,
      project.value.screenshots.map((item) => item.id),
    )
  }

  async function generate(format: string, gap: number, background: string) {
    if (!project.value) return
    loading.value = true
    try {
      if (roiSaveTimer) window.clearTimeout(roiSaveTimer)
      if (project.value.roi) await updateRoi(project.value.id, project.value.roi)
      exportUrl.value = await exportCollage(project.value.id, { format, gap, background })
      project.value = withUrls(await fetchProject(project.value.id))
    } finally {
      loading.value = false
    }
  }

  function disposeLocalUrls() {
    localUrls.forEach((url) => URL.revokeObjectURL(url))
    localUrls.clear()
  }

  return {
    project,
    screenshots,
    current,
    currentId,
    loading,
    exportUrl,
    roiError,
    ensureProject,
    addFiles,
    saveRoi,
    refreshStrips,
    patchImage,
    removeImage,
    saveOrder,
    generate,
    disposeLocalUrls,
  }
})
