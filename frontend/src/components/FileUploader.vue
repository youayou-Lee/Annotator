<!-- FileUploader.vue -->
<template>
  <div class="file-uploader">
    <el-upload
      class="upload-demo"
      :file-list="fileList"
      :before-upload="handleBeforeUpload"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :accept="accept"
      :auto-upload="false"
      drag
      multiple
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ tipText }}
        </div>
      </template>
    </el-upload>
    
    <div v-if="fileList.length" class="file-list">
      <el-card v-for="file in fileList" 
               :key="file.uid" 
               size="small" 
               class="file-card">
        <template #header>
          <div class="file-header">
            <el-icon><Document /></el-icon>
            {{ file.name }}
            <el-button
              type="danger"
              size="small"
              circle
              @click="handleRemove(file)"
              class="delete-button"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </template>
        <el-tag size="small" v-if="file.size">
          {{ formatFileSize(file.size) }}
        </el-tag>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits, defineProps } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadRawFile } from 'element-plus'
import {
  Document,
  UploadFilled,
  Delete
} from '@element-plus/icons-vue'

const props = defineProps({
  accept: {
    type: String,
    default: '*' // 默认接受所有文件类型，由父组件控制具体限制
  },
  maxSize: {
    type: Number,
    default: 100 // MB
  },
  tipText: {
    type: String,
    default: '请上传文件'
  },
  fileValidation: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['update:fileList', 'file-selected', 'file-removed'])

const fileList = ref<any[]>([])

// 处理文件上传前的验证
const handleBeforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 文件大小检查
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize}MB!`)
    return false
  }

  // 使用外部传入的验证函数
  if (props.fileValidation) {
    const validationResult = props.fileValidation(file)
    if (validationResult !== true) {
      ElMessage.error(typeof validationResult === 'string' ? validationResult : '文件验证失败')
      return false
    }
  }

  return false // 阻止自动上传
}

// 处理文件改变
const handleChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.status === 'ready') {
    // 直接使用 el-upload 组件的 fileList
    fileList.value = uploadFile.raw ? [...fileList.value, uploadFile] : fileList.value
    emit('update:fileList', fileList.value.map(file => file.raw))
    emit('file-selected', uploadFile.raw)
  }
}

// 处理文件移除
const handleRemove = (file: any) => {
  fileList.value = fileList.value.filter(item => item.uid !== file.uid)
  emit('update:fileList', fileList.value.map(file => file.raw))
  emit('file-removed', file.raw)
}

// 处理超出文件限制
const handleExceed: UploadProps['onExceed'] = (files) => {
  ElMessage.warning('每次只能上传一个文件')
}

// 文件大小格式化
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-demo {
  width: 100%;
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
}

.file-list {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.file-card {
  margin-bottom: 8px;
}

.file-header {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.delete-button {
  margin-left: auto;
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