<template>
  <aside class="sidebar">
    <div class="panel-title">图片列表</div>
    <VueDraggable v-model="localItems" class="image-list" :animation="150" handle=".drag-handle" @end="emitOrder">
      <button
        v-for="item in localItems"
        :key="item.id"
        class="image-row"
        :class="{ active: item.id === currentId }"
        @click="$emit('select', item.id)"
      >
        <span class="drag-handle">☰</span>
        <img v-if="item.preview_url || item.local_url" :src="item.preview_url || item.local_url" alt="" loading="lazy" />
        <span v-else class="thumb-fallback">{{ item.filename.slice(0, 1).toUpperCase() }}</span>
        <span class="meta">
          <strong>{{ item.order.toString().padStart(2, '0') }}</strong>
          <small>{{ item.filename }}</small>
        </span>
        <el-tag v-if="item.is_cover" size="small" type="success">封面</el-tag>
      </button>
    </VueDraggable>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import type { ScreenshotItem } from '../types'

const props = defineProps<{ items: ScreenshotItem[]; currentId?: string }>()
const emit = defineEmits<{ select: [id: string]; reorder: [items: ScreenshotItem[]] }>()
const localItems = ref<ScreenshotItem[]>([])

watch(
  () => props.items,
  (items) => {
    localItems.value = [...items]
  },
  { immediate: true },
)

function emitOrder() {
  emit('reorder', localItems.value)
}
</script>
