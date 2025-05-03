<!-- FormatUploader.vue -->
<template>
  <div class="format-uploader">
    <el-card class="upload-card">
      <template #header>
        <div class="card-title">
          <span>文件格式化工具</span>
          <el-tooltip content="上传JSONL文件并选择格式化模板，系统会按照模板格式处理数据">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>

      <!-- 数据文件上传区域 -->
      <el-form label-position="top">
        <el-form-item label="上传JSONL文件">
          <el-upload
            class="upload-demo"
            :file-list="jsonlFileList"
            :before-upload="beforeJsonlUpload"
            :on-change="handleJsonlChange"
            :on-remove="onJsonlRemove"
            :limit="1"
            accept=".jsonl"
            :auto-upload="false"
            :on-exceed="handleExceed"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传 JSONL 格式文件
              </div>
            </template>
          </el-upload>
          <div v-if="jsonlFileList.length" class="file-info">
            <el-card size="small" class="file-card">
              <template #header>
                <div class="file-header">
                  <el-icon><Document /></el-icon>
                  {{ jsonlFileList[0].name }}
                </div>
              </template>
              <el-tag size="small" v-if="jsonlFileList[0].size">
                {{ formatFileSize(jsonlFileList[0].size) }}
              </el-tag>
            </el-card>
          </div>
        </el-form-item>

        <!-- 模板选择区域 -->
        <el-form-item label="选择格式化模板">
          <el-radio-group v-model="templateMode" class="template-mode">
            <el-radio label="default">使用默认模板</el-radio>
            <el-radio label="custom">上传自定义模板</el-radio>
          </el-radio-group>

          <div v-if="templateMode === 'custom'" class="custom-template">
            <el-upload
              class="upload-demo"
              :file-list="templateFileList"
              :before-upload="beforeTemplateUpload"
              :on-change="handleTemplateChange"
              :on-remove="onTemplateRemove"
              :limit="1"
              accept=".json"
              :auto-upload="false"
              :on-exceed="handleExceed"
              drag
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽模板文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  请上传 JSON 格式的模板文件
                </div>
              </template>
            </el-upload>
          </div>

          <div v-if="templateMode === 'default' && defaultTemplate" class="template-preview">
            <el-collapse>
              <el-collapse-item title="查看默认模板结构" name="1">
                <pre>{{ JSON.stringify(defaultTemplate, null, 2) }}</pre>
              </el-collapse-item>
            </el-collapse>
          </div>
        </el-form-item>

        <!-- 处理按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            :loading="processing"
            @click="processFiles"
            :disabled="!canProcess"
          >
            开始处理
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 处理结果展示 -->
      <div v-if="processResult" class="process-result">
        <el-result
          :icon="processResult.success ? 'success' : 'error'"
          :title="processResult.message"
          :sub-title="processResult.output_path"
        >
          <template #extra>
            <div class="statistics">
              <el-statistic
                title="处理文档数"
                :value="processResult.document_count"
                class="stat-item"
              />
              <el-statistic
                title="成功数量"
                :value="processResult.success_count"
                value-style="color: #67c23a"
                class="stat-item"
              />
              <el-statistic
                title="失败数量"
                :value="processResult.error_count"
                value-style="color: #f56c6c"
                class="stat-item"
              />
            </div>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  Upload,
  InfoFilled,
  UploadFilled
} from '@element-plus/icons-vue'
import axios from 'axios'
import type { UploadProps, UploadRawFile } from 'element-plus'

export default defineComponent({
  name: 'FormatUploader',
  components: {
    Document,
    Upload,
    InfoFilled,
    UploadFilled
  },
  setup() {
    const jsonlFileList = ref<any[]>([])
    const templateFileList = ref<any[]>([])
    const templateMode = ref<'default' | 'custom'>('default')
    const defaultTemplate = ref(null)
    const processResult = ref(null)
    const processing = ref(false)

    // 计算属性：是否可以开始处理
    const canProcess = computed(() => {
      if (!jsonlFileList.value.length) return false
      if (templateMode.value === 'custom' && !templateFileList.value.length) return false
      return true
    })

    // 加载默认模板
    const loadDefaultTemplate = async () => {
      try {
        const response = await axios.get('/api/format/default-template')
        defaultTemplate.value = response.data
      } catch (error) {
        console.error('加载默认模板失败:', error)
        ElMessage.error('加载默认模板失败')
      }
    }

    // 处理超出文件限制
    const handleExceed: UploadProps['onExceed'] = (files) => {
      ElMessage.warning('每次只能上传一个文件')
    }

    // JSONL文件上传前检查
    const beforeJsonlUpload: UploadProps['beforeUpload'] = (file) => {
      const isJsonl = file.name.endsWith('.jsonl')
      if (!isJsonl) {
        ElMessage.error('只能上传 JSONL 格式文件!')
        return false
      }
      
      // 检查文件大小（限制为100MB）
      const isLt100M = file.size / 1024 / 1024 < 100
      if (!isLt100M) {
        ElMessage.error('文件大小不能超过 100MB!')
        return false
      }

      return false // 阻止自动上传
    }

    // 模板文件上传前检查
    const beforeTemplateUpload: UploadProps['beforeUpload'] = (file) => {
      const isJson = file.name.endsWith('.json')
      if (!isJson) {
        ElMessage.error('只能上传 JSON 格式文件!')
        return false
      }

      // 检查文件大小（限制为1MB）
      const isLt1M = file.size / 1024 / 1024 < 1
      if (!isLt1M) {
        ElMessage.error('模板文件大小不能超过 1MB!')
        return false
      }

      return false // 阻止自动上传
    }

    // JSONL文件更改处理
    const handleJsonlChange: UploadProps['onChange'] = (uploadFile) => {
      console.log('JSONL文件更改:', uploadFile)
      if (uploadFile.status === 'ready') {
        jsonlFileList.value = [uploadFile.raw]
      }
    }

    // 模板文件更改处理
    const handleTemplateChange: UploadProps['onChange'] = (uploadFile) => {
      console.log('模板文件更改:', uploadFile)
      if (uploadFile.status === 'ready') {
        templateFileList.value = [uploadFile.raw]
      }
    }

    // 移除JSONL文件
    const onJsonlRemove = () => {
      jsonlFileList.value = []
    }

    // 移除模板文件
    const onTemplateRemove = () => {
      templateFileList.value = []
    }

    // 文件大小格式化
    const formatFileSize = (bytes: number) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
    }

    // 处理文件
    const processFiles = async () => {
      if (!canProcess.value) return

      const formData = new FormData()
      
      // 确保文件对象是有效的
      if (!jsonlFileList.value[0] || !(jsonlFileList.value[0] instanceof File)) {
        ElMessage.error('请选择有效的 JSONL 文件')
        return
      }

      formData.append('jsonl_file', jsonlFileList.value[0])
      
      if (templateMode.value === 'custom') {
        if (!templateFileList.value[0] || !(templateFileList.value[0] instanceof File)) {
          ElMessage.error('请选择有效的模板文件')
          return
        }
        formData.append('template_file', templateFileList.value[0])
      }

      processing.value = true
      try {
        const response = await axios.post('/api/format/process', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          // 添加上传进度处理
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
              console.log('上传进度：', percentCompleted)
            }
          }
        })
        processResult.value = response.data
        if (response.data.success) {
          ElMessage.success('文件处理成功')
        } else {
          ElMessage.error(response.data.message || '文件处理失败')
        }
      } catch (error: any) {
        console.error('文件处理失败:', error)
        ElMessage.error(error.response?.data?.detail || '文件处理失败')
        processResult.value = {
          success: false,
          message: error.response?.data?.detail || '处理失败',
          document_count: 0,
          success_count: 0,
          error_count: 0
        }
      } finally {
        processing.value = false
      }
    }

    // 组件挂载时加载默认模板
    loadDefaultTemplate()

    return {
      jsonlFileList,
      templateFileList,
      templateMode,
      defaultTemplate,
      processResult,
      processing,
      canProcess,
      beforeJsonlUpload,
      beforeTemplateUpload,
      onJsonlRemove,
      onTemplateRemove,
      formatFileSize,
      processFiles,
      handleExceed,
      handleJsonlChange,
      handleTemplateChange
    }
  }
})
</script>

<style scoped>
.format-uploader {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-info {
  margin-top: 16px;
}

.file-card {
  margin-bottom: 16px;
}

.file-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-mode {
  margin-bottom: 16px;
}

.custom-template {
  margin-top: 16px;
}

.template-preview {
  margin-top: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

.template-preview pre {
  padding: 16px;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
  font-family: 'Courier New', Courier, monospace;
}

.process-result {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.statistics {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
}

.upload-demo {
  width: 100%;
}

.el-upload__text {
  margin: 10px 0;
}

.el-upload__text em {
  color: var(--el-color-primary);
  font-style: normal;
}

.el-upload__tip {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
}
</style>