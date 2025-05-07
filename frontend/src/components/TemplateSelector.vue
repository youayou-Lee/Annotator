<!-- TemplateSelector.vue -->
<template>
  <div class="template-selector">
    <el-tabs v-model="templateMode" v-if="showTabs">
      <el-tab-pane :label="systemTemplateLabel" name="system">
        <el-select 
          v-model="selectedTemplate" 
          :placeholder="placeholder"
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
        
        <!-- 模板预览 -->
        <div v-if="selectedTemplate && templateContent" class="template-preview">
          <el-collapse>
            <el-collapse-item :title="previewTitle" name="1">
              <pre class="code-preview">{{ templateContent }}</pre>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-tab-pane>

      <el-tab-pane label="自定义模板" name="custom" v-if="allowCustom">
        <FileUploader
          v-model:fileList="customTemplate"
          :accept="fileAccept"
          :maxSize="maxFileSize"
          :tipText="uploadTipText"
          :fileValidation="validateFile"
          @file-selected="handleTemplateSelected"
          @file-removed="handleTemplateRemoved"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 不显示tabs时只显示系统模板选择 -->
    <template v-else>
      <el-select 
        v-model="selectedTemplate" 
        :placeholder="placeholder"
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

      <!-- 模板预览 -->
      <div v-if="selectedTemplate && templateContent && showPreview" class="template-preview">
        <el-collapse>
          <el-collapse-item :title="previewTitle" name="1">
            <pre class="code-preview">{{ templateContent }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import FileUploader from './FileUploader.vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value: string) => ['format', 'task'].includes(value)
  },
  showTabs: {
    type: Boolean,
    default: true
  },
  allowCustom: {
    type: Boolean,
    default: true
  },
  placeholder: {
    type: String,
    default: '请选择模板'
  },
  systemTemplateLabel: {
    type: String,
    default: '系统模板'
  },
  previewTitle: {
    type: String,
    default: '查看模板内容'
  },
  fileAccept: {
    type: String,
    default: '.py'
  },
  maxFileSize: {
    type: Number,
    default: 1
  },
  uploadTipText: {
    type: String,
    default: '请上传模板文件'
  },
  showPreview: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:template', 'update:customFile'])

// 状态
const templateMode = ref('system')
const selectedTemplate = ref('')
const customTemplate = ref<any[]>([])
const templateContent = ref(null)
const systemTemplates = ref([])

// 监听模板选择变化
watch(selectedTemplate, (newTemplateId) => {
  if (newTemplateId) {
    loadTemplateContent(newTemplateId)
  } else {
    templateContent.value = null
  }
  emit('update:template', newTemplateId)
})

// 监听自定义模板变化
watch(customTemplate, (newFiles) => {
  emit('update:customFile', newFiles[0])
})

// 加载系统预设模板列表
const loadSystemTemplates = async () => {
  try {
    const endpoint = props.type === 'format' ? '/api/format/template' : '/api/templates'
    const response = await axios.get(endpoint)
    const templates = response.data.templates || []  // 从 response.data.templates 获取模板列表
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

// 加载模板内容
const loadTemplateContent = async (templateName: string) => {
  if (!templateName) return
  
  try {
    const endpoint = props.type === 'format' 
      ? `/api/format/template/${templateName}/content`
      : `/api/templates/${templateName}/content`
    const response = await axios.get(endpoint)
    templateContent.value = props.type === 'format'
      ? response.data.content.replace(/\\n/g, '\n')
      : JSON.stringify(response.data, null, 2)
  } catch (error) {
    console.error('加载模板内容失败:', error)
    ElMessage.error('加载模板内容失败')
  }
}

// 文件处理函数
const handleTemplateSelected = (file: File) => {
  emit('update:customFile', file)
}

const handleTemplateRemoved = () => {
  emit('update:customFile', null)
}

// 文件验证
const validateFile = (file: File) => {
  const extension = props.type === 'format' ? '.py' : '.json'
  if (!file.name.endsWith(extension)) {
    return `只能上传 ${extension} 格式文件!`
  }
  return true
}

// 组件挂载时加载模板
onMounted(() => {
  loadSystemTemplates()
})
</script>

<style scoped>
.template-selector {
  width: 100%;
}

.template-preview {
  margin-top: 16px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

.code-preview {
  padding: 16px;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 12px;
  font-family: 'Courier New', Courier, monospace;
}
</style>