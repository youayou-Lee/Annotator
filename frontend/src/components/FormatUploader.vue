<!-- FormatUploader.vue -->
<template>
  <div class="format-uploader">
    <el-card class="upload-card">
      <template #header>
        <div class="card-title">
          <span>文件格式化工具</span>
          <el-tooltip content="上传数据文件，选择格式化模板，系统会按照模板格式处理数据">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
      </template>

      <el-form label-position="top">
        <!-- 文件上传区域 -->
        <el-form-item label="步骤 1: 上传文件">
          <FileUploader
            v-model:fileList="uploadedFile"
            :accept="'.json,.jsonl'"
            :maxSize="100"
            :tipText="'请上传需要格式化的 JSON 或 JSONL 文件'"
            @file-selected="handleFileSelected"
            @file-removed="handleFileRemoved"
          />
        </el-form-item>

        <!-- 模板选择区域 -->
        <el-form-item label="步骤 2: 选择格式化模板">
          <TemplateSelector
            type="format"
            v-model:template="selectedTemplate"
            v-model:customFile="customTemplateFile"
            :uploadTipText="'请上传 py 格式的模板文件'"
          />
        </el-form-item>

        <!-- 处理按钮 -->
        <el-form-item label="步骤 3: 开始格式化">
          <el-button
            type="primary"
            :loading="processing"
            @click="processFiles"
            :disabled="!canProcess"
            style="width: 100%"
          >
            {{ processing ? '处理中...' : '开始格式化' }}
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

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import FileUploader from './FileUploader.vue'
import TemplateSelector from './TemplateSelector.vue'

// 状态定义
const uploadedFile = ref<any[]>([])
const selectedTemplate = ref('')
const customTemplateFile = ref(null)
const processResult = ref(null)
const processing = ref(false)

// 计算属性：是否可以开始处理
const canProcess = computed(() => {
  if (!uploadedFile.value.length) return false
  if (!selectedTemplate.value && !customTemplateFile.value) return false
  return true
})

// 文件处理函数
const handleFileSelected = (file: File) => {
  console.log('选择了文件:', file.name)
}

const handleFileRemoved = () => {
  console.log('移除了文件')
}

// 处理文件
const processFiles = async () => {
  if (!canProcess.value) return

  const formData = new FormData()
  
  if (!uploadedFile.value[0]) {
    ElMessage.error('请选择有效的文件')
    return
  }
  
  formData.append('jsonl_file', uploadedFile.value[0])
  
  if (customTemplateFile.value) {
    formData.append('template_file', customTemplateFile.value)
  } else if (selectedTemplate.value) {
    formData.append('template_name', selectedTemplate.value)
  }

  processing.value = true
  try {
    const response = await axios.post('/api/format/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
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
</style>



