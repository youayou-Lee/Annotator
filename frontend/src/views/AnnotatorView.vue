<template>
  <div class="annotator-container">
    <el-container>
      <el-header>
        <div class="header-left">
          <h2>文书标注系统</h2>
          <el-tag type="success" class="task-tag">任务ID: {{ taskId }}</el-tag>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="saveAnnotation">保存标注</el-button>
          <el-button @click="goBack">返回任务列表</el-button>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <el-col :span="16">
            <!-- 文书内容展示 -->
            <el-card class="document-card">
              <template #header>
                <div class="card-header">
                  <span>文书内容</span>
                  <el-button-group>
                    <el-button size="small" @click="prevDocument" :disabled="currentPage <= 1">上一页</el-button>
                    <el-button size="small" @click="nextDocument" :disabled="currentPage >= totalDocuments">下一页</el-button>
                  </el-button-group>
                </div>
              </template>
              <div class="document-content">
                <div v-for="(value, key) in currentDocument" :key="key" class="document-item">
                  <span class="item-label">{{ key }}:</span>
                  <span class="item-value">{{ value }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <!-- 标注表单 -->
            <el-card class="annotation-card">
              <template #header>
                <div class="card-header">
                  <span>标注信息</span>
                  <el-tag type="info">第 {{ currentPage }} 页，共 {{ totalDocuments }} 页</el-tag>
                </div>
              </template>
              <el-form :model="annotationForm" label-width="120px">
                <el-form-item 
                  v-for="field in annotationFields" 
                  :key="field.key"
                  :label="field.label"
                  :prop="field.key"
                >
                  <el-input
                    v-if="field.type === 'text'"
                    v-model="annotationForm[field.key]"
                    type="textarea"
                    :rows="3"
                    :placeholder="field.placeholder"
                  />
                  <el-select
                    v-else-if="field.type === 'select'"
                    v-model="annotationForm[field.key]"
                    :placeholder="'请选择' + field.label"
                  >
                    <el-option
                      v-for="option in field.options"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                  <el-radio-group
                    v-else-if="field.type === 'radio'"
                    v-model="annotationForm[field.key]"
                  >
                    <el-radio
                      v-for="option in field.options"
                      :key="option.value"
                      :label="option.value"
                    >
                      {{ option.label }}
                    </el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </el-card>
            
            <!-- 标注历史 -->
            <el-card class="history-card">
              <template #header>
                <div class="card-header">
                  <span>标注历史</span>
                </div>
              </template>
              <el-timeline>
                <el-timeline-item
                  v-for="(history, index) in annotationHistory"
                  :key="index"
                  :timestamp="history.timestamp"
                  :type="history.type"
                >
                  {{ history.content }}
                </el-timeline-item>
              </el-timeline>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// 状态
const currentDocument = ref({})
const annotationForm = ref({})
const currentPage = ref(1)
const totalDocuments = ref(0)
const taskId = ref('')
const annotationHistory = ref([])

// 标注字段配置
const annotationFields = ref([
  {
    key: 'review_result',
    label: '审查结果',
    type: 'text',
    placeholder: '请输入审查结果...'
  },
  {
    key: 'confidence',
    label: '置信度',
    type: 'select',
    options: [
      { label: '高', value: 'high' },
      { label: '中', value: 'medium' },
      { label: '低', value: 'low' }
    ]
  },
  {
    key: 'review_type',
    label: '审查类型',
    type: 'radio',
    options: [
      { label: '形式审查', value: 'formal' },
      { label: '实质审查', value: 'substantive' }
    ]
  },
  {
    key: 'comments',
    label: '备注',
    type: 'text',
    placeholder: '请输入备注信息...'
  }
])

// 方法
const loadDocument = async (page: number) => {
  try {
    const response = await axios.get(`/api/tasks/${taskId.value}/documents/${page}`)
    currentDocument.value = response.data.document
    annotationForm.value = response.data.annotation || {}
    totalDocuments.value = response.data.total
  } catch (error) {
    ElMessage.error('加载文档失败')
  }
}

const saveAnnotation = async () => {
  try {
    await axios.post(`/api/tasks/${taskId.value}/annotations/${currentDocument.value.id}`, annotationForm.value)
    ElMessage.success('保存成功')
    
    // 添加标注历史
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: `已保存第 ${currentPage.value} 页的标注`,
      type: 'success'
    })
  } catch (error) {
    ElMessage.error('保存失败')
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: `保存第 ${currentPage.value} 页标注失败`,
      type: 'danger'
    })
  }
}

const prevDocument = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadDocument(currentPage.value)
  }
}

const nextDocument = () => {
  if (currentPage.value < totalDocuments.value) {
    currentPage.value++
    loadDocument(currentPage.value)
  }
}

const goBack = () => {
  router.push('/admin')
}

// 生命周期
onMounted(() => {
  // 从路由参数获取任务ID
  taskId.value = route.params.taskId as string
  if (!taskId.value) {
    ElMessage.error('未找到任务ID')
    router.push('/admin')
    return
  }
  loadDocument(1)
})
</script>

<style scoped lang="scss">
.annotator-container {
  height: 100vh;
  padding: 20px;
  
  .el-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .task-tag {
        margin-left: 10px;
      }
    }
    
    .header-right {
      display: flex;
      gap: 10px;
    }
  }
  
  .document-card, .annotation-card, .history-card {
    height: calc(100vh - 200px);
    overflow-y: auto;
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .document-content {
    .document-item {
      margin-bottom: 10px;
      
      .item-label {
        font-weight: bold;
        margin-right: 10px;
      }
    }
  }
  
  .history-card {
    height: 300px;
  }
}
</style> 