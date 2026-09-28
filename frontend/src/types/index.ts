export interface RoiConfig {
  x: number
  y: number
  width: number
  height: number
}

export interface ScreenshotItem {
  id: string
  filename: string
  order: number
  original_path: string
  preview_path?: string
  cropped_path?: string
  original_url?: string
  local_url?: string
  preview_url?: string
  cropped_url?: string
  selected: boolean
  is_cover: boolean
}

export interface Project {
  id: string
  name: string
  roi?: RoiConfig
  screenshots: ScreenshotItem[]
  export_format: string
  gap: number
  background: string
}
