<template>
  <div class="app-shell" v-loading="store.loading">
    <header class="topbar">
      <div>
        <h1>Subtitle Collage</h1>
        <p>影视字幕截图自动拼贴工具 MVP</p>
      </div>
      <ImageUploader @upload="upload" />
    </header>

    <main class="workspace">
      <ScreenshotList
        :items="store.screenshots"
        :current-id="store.currentId"
        @select="store.currentId = $event"
        @reorder="store.saveOrder"
      />

      <div class="center-stack">
        <ScreenshotPreview :item="store.current" :roi="store.project?.roi" @change="store.saveRoi" />
        <ExportItemsTable :items="store.screenshots" @toggle="toggleSelected" />
      </div>

      <aside class="settings">
        <div class="panel-title">参数面板</div>
        <el-form label-position="top">
          <el-form-item label="当前图片">
            <el-select v-model="store.currentId" placeholder="选择图片">
              <el-option v-for="item in store.screenshots" :key="item.id" :label="item.filename" :value="item.id" />
            </el-select>
          </el-form-item>

          <el-form-item label="顶部封面">
            <el-button :disabled="!store.current" @click="setCover">设为顶部封面</el-button>
          </el-form-item>

          <el-form-item label="字幕区域">
            <el-slider v-model="subtitleHeight" :min="5" :max="45" :step="1" @input="setSubtitleHeight" />
            <div v-if="store.roiError" class="form-error">{{ store.roiError }}</div>
          </el-form-item>

          <el-form-item label="字幕条预览">
            <el-button :disabled="store.screenshots.length === 0 || !store.project?.roi" @click="refreshStrips">
              刷新字幕条
            </el-button>
          </el-form-item>

          <el-form-item label="拼贴间距">
            <el-input-number v-model="gap" :min="0" :max="200" />
          </el-form-item>

          <el-form-item label="背景色">
            <el-color-picker v-model="background" />
          </el-form-item>

          <el-form-item label="输出格式">
            <el-segmented v-model="format" :options="['png', 'jpg']" />
          </el-form-item>

          <el-form-item>
            <el-button type="success" :disabled="store.screenshots.length === 0" @click="generateCollage">
              生成长图
            </el-button>
          </el-form-item>

          <el-form-item>
            <el-button type="danger" plain :disabled="!store.current" @click="removeCurrent">删除当前图片</el-button>
          </el-form-item>
        </el-form>

        <ExportPreview :url="store.exportUrl" />
      </aside>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import ImageUploader from '../components/ImageUploader.vue'
import ScreenshotList from '../components/ScreenshotList.vue'
import ScreenshotPreview from '../components/ScreenshotPreview.vue'
import ExportItemsTable from '../components/ExportItemsTable.vue'
import ExportPreview from '../components/ExportPreview.vue'
import { useProjectStore } from '../stores/project'

const store = useProjectStore()
const gap = ref(12)
const background = ref('#000000')
const format = ref('png')
const subtitleHeight = ref(25)

onMounted(() => {
  store
    .ensureProject()
    .then(() => {
      if (!store.project?.roi) setSubtitleHeight(subtitleHeight.value)
    })
    .catch(showError)
})

onBeforeUnmount(() => {
  store.disposeLocalUrls()
})

watch(
  () => store.project?.roi?.height,
  (height) => {
    if (typeof height === 'number') subtitleHeight.value = Math.round(height * 100)
  },
  { immediate: true },
)

async function upload(files: File[]) {
  try {
    await store.addFiles(files)
  } catch (error) {
    showError(error)
  }
}

function setSubtitleHeight(value: number | number[]) {
  const height = (Array.isArray(value) ? value[0] : value) / 100
  store.saveRoi({ x: 0, y: 1 - height, width: 1, height }).catch(showError)
}

function setCover() {
  if (!store.current) return
  store.patchImage(store.current.id, { is_cover: true }).catch(showError)
}

function toggleSelected(id: string, selected: boolean) {
  store.patchImage(id, { selected }).catch(showError)
}

function refreshStrips() {
  store.refreshStrips().catch(showError)
}

function generateCollage() {
  store.generate(format.value, gap.value, background.value).catch(showError)
}

function removeCurrent() {
  if (!store.current) return
  store.removeImage(store.current.id).catch(showError)
}

function showError(error: unknown) {
  ElMessage.error(error instanceof Error ? error.message : '操作失败')
}
</script>
