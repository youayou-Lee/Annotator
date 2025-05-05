<!-- FileUploader.vue -->
<template>
  <div class="file-uploader">
    <el-upload
      class="upload-demo"
      :file-list="fileList"
      :before-upload="handleBeforeUpload"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :limit="1"
      :accept="accept"
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
          {{ tipText }}
        </div>
      </template>
    </el-upload>
    
    <div v-if="fileList.length" class="file-info">
      <el-card size="small" class="file-card">
        <template #header>
          <div class="file-header">
            <el-icon><Document /></el-icon>
            {{ fileList[0].name }}
          </div>
        </template>
        <el-tag size="small" v-if="fileList[0].size">
          {{ formatFileSize(fileList[0].size) }}
        </el-tag>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineEmits, defineProps } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadProps, UploadRawFile } from 'element-plus'
import {
  Document,
  UploadFilled
} from '@element-plus/icons-vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.json,.jsonl'
  },
  maxSize: {
    type: Number,
    default: 100 // MB
  },
  tipText: {
    type: String,
    default: '支持上传 JSON 或 JSONL 格式文件'
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

  // 自定义验证
  if (props.fileValidation) {
    const validationResult = props.fileValidation(file)
    if (validationResult !== true) {
      ElMessage.error(validationResult || '文件验证失败')
      return false
    }
  }

  return false // 阻止自动上传
}

// 处理文件改变
const handleChange: UploadProps['onChange'] = (uploadFile) => {
  if (uploadFile.status === 'ready') {
    fileList.value = [uploadFile.raw]
    emit('update:fileList', fileList.value)
    emit('file-selected', uploadFile.raw)
  }
}

// 处理文件移除
const handleRemove = () => {
  fileList.value = []
  emit('update:fileList', fileList.value)
  emit('file-removed')
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