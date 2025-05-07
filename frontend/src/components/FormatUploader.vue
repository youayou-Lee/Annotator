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
            :fileValidation="validateJsonFile"
            @file-selected="handleFileSelected"
            @file-removed="handleFileRemoved"
          />
        </el-form-item>

        <!-- 模板选择区域 -->
        <el-form-item label="步骤 2: 选择格式化模板">
          <el-tabs v-model="templateMode" class="template-tabs">
            <el-tab-pane label="系统模板" name="system">
              <el-select 
                v-model="selectedTemplate" 
                placeholder="请选择系统预设模板"
                style="width: 100%"
              >
                <el-option
                  v-for="template in systemTemplates"
                  :key="template.name"
                  :label="template.name"
                  :value="template.id"
                >
                  <span>{{ template.name }}</span>
                  <small style="color: #8c8c8c; margin-left: 8px">{{ template.description }}</small>
                </el-option>
              </el-select>
              <div v-if="selectedTemplate && defaultTemplate" class="template-preview">
                <el-collapse>
                  <el-collapse-item title="查看模板结构" name="1">
                    <pre class="code-preview">{{ defaultTemplate }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="自定义模板" name="custom">
              <FileUploader
                v-model:fileList="customTemplate"
                :accept="'.py'"
                :maxSize="1"
                :tipText="'请上传 py 格式的模板文件'"
                :fileValidation="validatePythonFile"
                @file-selected="handleTemplateSelected"
                @file-removed="handleTemplateRemoved"
              />
            </el-tab-pane>
          </el-tabs>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  InfoFilled
} from '@element-plus/icons-vue'
import axios from 'axios'
import FileUploader from './FileUploader.vue'

// 状态定义
const uploadedFile = ref<any[]>([])
const customTemplate = ref<any[]>([])
const templateMode = ref('system')
const selectedTemplate = ref('')
const defaultTemplate = ref(null)
const processResult = ref(null)
const processing = ref(false)
const systemTemplates = ref([
  { id: 'default', name: '默认模板', description: '系统默认的格式化模板' }
])

// 计算属性：是否可以开始处理
const canProcess = computed(() => {
  if (!uploadedFile.value.length) return false
  if (templateMode.value === 'system' && !selectedTemplate.value) return false
  if (templateMode.value === 'custom' && !customTemplate.value.length) return false
  return true
})

// 监听选中模板的变化 -- 在这里添加 watch
watch(selectedTemplate, (newTemplateId) => {
  if (newTemplateId) {
    loadDefaultTemplate(newTemplateId)
  } else {
    defaultTemplate.value = null
  }
})

// 加载系统预设模板列表
const loadSystemTemplates = async () => {
  try {
    const response = await axios.get('/api/format/template')
    const templates = response.data || []
    systemTemplates.value = templates.map((t: string) => ({
      id: t,
      name: t,
      description: '系统预设模板'
    }))
  } catch (error) {
    console.error('加载系统模板列表失败:', error)
    ElMessage.error('加载系统模板列表失败')
  }
}

// 加载默认模板
const loadDefaultTemplate = async (templateName: string) => {
  if (!templateName) return
  
  try {
    const response = await axios.get(`/api/format/template/${templateName}/content`)
    defaultTemplate.value = response.data.content.replace(/\\n/g, '\n')
  } catch (error) {
    console.error('加载模板内容失败:', error)
    ElMessage.error('加载模板内容失败')
  }
}

// 文件处理函数
const handleFileSelected = (file: File) => {
  console.log('选择了文件:', file.name)
}

const handleFileRemoved = () => {
  console.log('移除了文件')
}

const handleTemplateSelected = (file: File) => {
  console.log('选择了模板:', file.name)
}

const handleTemplateRemoved = () => {
  console.log('移除了模板')
}

// 模板文件验证
const validateTemplateFile = (file: File) => {
  const isJson = file.name.endsWith('.py')
  if (!isJson) {
    return '只能上传 PY 格式文件!'
  }
  return true
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
  
  if (templateMode.value === 'custom') {
    if (!customTemplate.value[0]) {
      ElMessage.error('请选择有效的模板文件')
      return
    }
    formData.append('template_file', customTemplate.value[0])
  } else if (templateMode.value === 'system' && selectedTemplate.value) {
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

// 组件挂载时加载模板
onMounted(() => {
  loadSystemTemplates()
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

.template-tabs {
  width: 100%;
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

.code-preview {
  padding: 16px;
  margin: 0;
  white-space: pre;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #f8f9fa;
  border-radius: 4px;
  color: #333;
}

</style>



