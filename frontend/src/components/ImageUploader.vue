<template>
  <div class="uploader" @dragover.prevent @drop.prevent="onDrop">
    <input ref="inputRef" class="file-input" type="file" multiple accept="image/png,image/jpeg,image/webp" @change="onPick" />
    <el-button type="primary" @click="inputRef?.click()">导入图片</el-button>
    <span>支持 PNG、JPG、JPEG、WEBP，最多 50 张</span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ upload: [files: File[]] }>()
const inputRef = ref<HTMLInputElement>()
const allowed = new Set(['image/png', 'image/jpeg', 'image/webp'])

function filterFiles(list: FileList | File[]) {
  return Array.from(list).filter((file) => allowed.has(file.type) && file.size <= 15 * 1024 * 1024)
}

function onPick(event: Event) {
  const target = event.target as HTMLInputElement
  emit('upload', filterFiles(target.files ?? []))
  target.value = ''
}

function onDrop(event: DragEvent) {
  emit('upload', filterFiles(event.dataTransfer?.files ?? []))
}
</script>

