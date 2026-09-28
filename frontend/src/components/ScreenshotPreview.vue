<template>
  <section class="preview-panel">
    <div class="preview-toolbar">
      <div>
        <strong>{{ item?.filename || '等待导入图片' }}</strong>
        <span v-if="roi">字幕高度 {{ percent(roi.height) }}</span>
      </div>
      <el-button :disabled="!item" @click="resetRoi">重置字幕框</el-button>
    </div>
    <div ref="stageRef" class="preview-stage">
      <div
        v-if="imageUrl"
        ref="imageLayerRef"
        class="image-layer"
        :style="imageLayerStyle"
        @pointerdown="startResize"
      >
        <img ref="imageRef" :src="imageUrl" alt="" draggable="false" @load="measureImage" />
        <div v-if="roi" class="roi-box" :style="roiStyle" @pointerdown.stop="startResize">
          <span></span>
        </div>
      </div>
      <div v-else class="empty-state">导入截图后，拖动底部字幕框上沿调整高度</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { RoiConfig, ScreenshotItem } from '../types'

const props = defineProps<{ item?: ScreenshotItem; roi?: RoiConfig }>()
const emit = defineEmits<{ change: [roi: RoiConfig] }>()
const stageRef = ref<HTMLElement>()
const imageRef = ref<HTMLImageElement>()
const imageLayerRef = ref<HTMLElement>()
const naturalSize = ref({ width: 16, height: 9 })
const layerSize = ref({ width: 0, height: 0 })
let resizeObserver: ResizeObserver | undefined

const fallbackRoi: RoiConfig = { x: 0, y: 0.75, width: 1, height: 0.25 }
const activeRoi = computed(() => props.roi ?? fallbackRoi)
const imageUrl = computed(() => props.item?.local_url || props.item?.original_url || props.item?.preview_url || '')
const imageLayerStyle = computed(() => ({
  width: `${layerSize.value.width}px`,
  height: `${layerSize.value.height}px`,
}))
const roiStyle = computed(() => ({
  left: '0%',
  top: `${(1 - activeRoi.value.height) * 100}%`,
  width: '100%',
  height: `${activeRoi.value.height * 100}%`,
}))

function percent(value: number) {
  return `${Math.round(value * 100)}%`
}

function resetRoi() {
  emit('change', fallbackRoi)
}

function point(event: PointerEvent) {
  const rect = imageLayerRef.value?.getBoundingClientRect()
  if (!rect) return { x: 0, y: 0 }
  return {
    x: Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)),
    y: Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height)),
  }
}

function measureImage() {
  if (imageRef.value?.naturalWidth && imageRef.value?.naturalHeight) {
    naturalSize.value = {
      width: imageRef.value.naturalWidth,
      height: imageRef.value.naturalHeight,
    }
  }
  measureStage()
}

function measureStage() {
  const rect = stageRef.value?.getBoundingClientRect()
  if (!rect) return
  const imageRatio = naturalSize.value.width / naturalSize.value.height
  const stageRatio = rect.width / rect.height
  if (imageRatio >= stageRatio) {
    layerSize.value = {
      width: rect.width,
      height: rect.width / imageRatio,
    }
  } else {
    layerSize.value = {
      width: rect.height * imageRatio,
      height: rect.height,
    }
  }
}

function startResize(event: PointerEvent) {
  if (!props.item) return
  const onMove = (moveEvent: PointerEvent) => {
    const current = point(moveEvent)
    const height = Math.min(0.8, Math.max(0.03, 1 - current.y))
    emit('change', { x: 0, y: 1 - height, width: 1, height })
  }
  const onUp = () => {
    window.removeEventListener('pointermove', onMove)
    window.removeEventListener('pointerup', onUp)
  }
  window.addEventListener('pointermove', onMove)
  window.addEventListener('pointerup', onUp)
  onMove(event)
}

onMounted(() => {
  resizeObserver = new ResizeObserver(measureStage)
  if (stageRef.value) resizeObserver.observe(stageRef.value)
  nextTick(measureStage)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
})

watch(imageUrl, () => nextTick(measureStage))
</script>
