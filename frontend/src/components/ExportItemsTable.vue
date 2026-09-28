<template>
  <section class="export-items-panel">
    <div class="panel-title">导出图片</div>
    <el-table :data="items" height="100%" stripe>
      <el-table-column prop="order" label="#" width="48" />
      <el-table-column label="图片" width="132">
        <template #default="{ row }">
          <img class="strip-thumb" :src="row.preview_url || row.original_url" alt="" />
        </template>
      </el-table-column>
      <el-table-column label="文件" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="file-cell">
            <strong>{{ row.filename }}</strong>
            <span v-if="row.is_cover" class="muted">完整封面</span>
          </span>
        </template>
      </el-table-column>
      <el-table-column label="字幕条" width="132">
        <template #default="{ row }">
          <img v-if="row.cropped_url && !row.is_cover" class="strip-thumb" :src="row.cropped_url" alt="" />
          <span v-else class="muted">{{ row.is_cover ? '封面跳过' : '生成后显示' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="导出" width="72" fixed="right">
        <template #default="{ row }">
          <el-switch v-model="row.selected" :disabled="row.is_cover" @change="$emit('toggle', row.id, row.selected)" />
        </template>
      </el-table-column>
    </el-table>
  </section>
</template>

<script setup lang="ts">
import type { ScreenshotItem } from '../types'

defineProps<{ items: ScreenshotItem[] }>()
defineEmits<{
  toggle: [id: string, selected: boolean]
}>()
</script>
