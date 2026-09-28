<template>
  <section class="export-panel">
    <div class="panel-title">导出预览</div>
    <div v-if="url" class="export-preview">
      <img :src="`${url}?t=${cacheKey}`" alt="" />
    </div>
    <div v-else class="empty-export">生成后显示长图预览</div>
    <a v-if="url" class="download-link" :href="url" download>下载长图</a>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ url: string }>()
const cacheKey = computed(() => encodeURIComponent(props.url + Date.now()))
</script>

