<template>
  <div class="admin-container">
    <el-container>
      <el-aside width="200px">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          @select="handleMenuSelect"
        >
          <el-menu-item index="filter">
            <el-icon><Filter /></el-icon>
            <span>数据过滤</span>
          </el-menu-item>
          <el-menu-item index="format">
            <el-icon><Document /></el-icon>
            <span>格式化存储</span>
          </el-menu-item>
          <el-menu-item index="tasks">
            <el-icon><List /></el-icon>
            <span>任务管理</span>
          </el-menu-item>
          <el-menu-item index="ai-review">
            <el-icon><Monitor /></el-icon>
            <span>AI审查</span>
          </el-menu-item>
          <el-menu-item index="training">
            <el-icon><Connection /></el-icon>
            <span>模型训练</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <!-- 数据过滤 -->
        <div v-if="activeMenu === 'filter'" class="filter-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>数据过滤</span>
              </div>
            </template>
            <el-form :model="filterForm" label-width="120px">
              <el-form-item label="选择文件">
                <el-select
                  v-model="filterForm.selectedFiles"
                  multiple
                  placeholder="请选择要过滤的文件"
                  style="width: 100%"
                >
                  <el-option
                    v-for="file in availableFiles"
                    :key="file"
                    :label="file"
                    :value="file"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="省份">
                <el-select v-model="filterForm.province" placeholder="请选择省份">
                  <el-option label="广东省" value="广东" />
                  <el-option label="北京市" value="北京" />
                  <!-- 更多选项 -->
                </el-select>
              </el-form-item>
              
              <el-form-item label="案件类型">
                <el-select v-model="filterForm.caseType" placeholder="请选择案件类型">
                  <el-option label="刑事一审" value="criminal_first" />
                  <el-option label="民事一审" value="civil_first" />
                  <!-- 更多选项 -->
                </el-select>
              </el-form-item>
              
              <el-form-item label="审级">
                <el-select v-model="filterForm.level" placeholder="请选择审级">
                  <el-option label="一审" value="一审" />
                  <el-option label="二审" value="二审" />
                  <el-option label="再审" value="再审" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="filterForm.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              
              <el-form-item label="案由">
                <el-select v-model="filterForm.caseReason" placeholder="请选择案由">
                  <el-option label="交通事故" value="交通事故" />
                  <el-option label="合同纠纷" value="合同纠纷" />
                  <!-- 更多选项 -->
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="handleFilter">开始过滤</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        
        <!-- 格式化存储 -->
        <div v-if="activeMenu === 'format'" class="format-section">
          <FormatUploader />
        </div>
        
        <!-- 任务管理 -->
        <div v-if="activeMenu === 'tasks'" class="tasks-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>任务管理</span>
                <el-button type="primary" @click="showCreateTaskDialog">创建任务</el-button>
              </div>
            </template>
            <el-table :data="tasks" style="width: 100%">
              <el-table-column prop="id" label="任务ID" width="180" />
              <el-table-column prop="name" label="任务名称" width="180" />
              <el-table-column prop="status" label="状态" />
              <el-table-column prop="created_at" label="创建时间" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button
                    size="small"
                    type="primary"
                    @click="startAnnotation(scope.row)"
                  >开始标注</el-button>
                  <el-button
                    size="small"
                    @click="handleEditTask(scope.row)"
                  >编辑</el-button>
                  <el-button
                    size="small"
                    type="warning"
                    @click="handleMergeAnnotations(scope.row)"
                    :disabled="scope.row.status !== 'pending'"
                  >合并标注</el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="handleDeleteTask(scope.row)"
                  >删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
        
        <!-- AI审查 -->
        <div v-if="activeMenu === 'ai-review'" class="ai-review-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>AI审查</span>
              </div>
            </template>
            <el-form :model="aiReviewForm" label-width="120px">
              <el-form-item label="任务">
                <el-select v-model="aiReviewForm.taskId" placeholder="请选择任务">
                  <el-option
                    v-for="task in tasks"
                    :key="task.id"
                    :label="task.name"
                    :value="task.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="提示模板">
                <el-input
                  v-model="aiReviewForm.promptTemplate"
                  type="textarea"
                  :rows="5"
                  placeholder="请输入提示模板"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleAIReview">开始审查</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
        
        <!-- 模型训练 -->
        <div v-if="activeMenu === 'training'" class="training-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>模型训练</span>
              </div>
            </template>
            <el-form :model="trainingForm" label-width="120px">
              <el-form-item label="任务">
                <el-select v-model="trainingForm.taskId" placeholder="请选择任务">
                  <el-option
                    v-for="task in tasks"
                    :key="task.id"
                    :label="task.name"
                    :value="task.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="训练比例">
                <el-slider
                  v-model="trainingForm.trainRatio"
                  :min="0.5"
                  :max="0.9"
                  :step="0.1"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleTraining">开始训练</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-main>
    </el-container>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createTaskDialogVisible"
      title="创建任务"
      width="50%"
    >
      <el-form :model="createTaskForm" label-width="120px">
        <el-form-item label="任务名称" required>
          <el-input v-model="createTaskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务描述" required>
          <el-input
            v-model="createTaskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="可标注字段" required>
          <el-table :data="createTaskForm.config" style="width: 100%">
            <el-table-column label="字段路径">
              <template #default="{ row }">
                <el-select
                  v-model="row.path"
                  filterable
                  allow-create
                  default-first-option
                  placeholder="请选择或输入字段路径"
                >
                  <el-option
                    v-for="field in defaultAnnotationFields"
                    :key="field"
                    :label="field"
                    :value="field"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="字段类型" width="150">
              <template #default="{ row }">
                <el-select v-model="row.type" placeholder="请选择字段类型">
                  <el-option label="文本" value="string" />
                  <el-option label="数字" value="number" />
                  <el-option label="布尔值" value="boolean" />
                  <el-option label="数组" value="array" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="removeField($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 10px;">
            <el-button type="primary" @click="addField">添加字段</el-button>
          </div>
        </el-form-item>
        <el-form-item label="数据文件" required>
          <el-upload
            class="upload-demo"
            action="/api/upload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :headers="{
              'Accept': 'application/json'
            }"
            :data="{
              type: 'document'
            }"
            :auto-upload="true"
            :show-file-list="true"
            :limit="1"
            name="file"
            accept=".json,.jsonl"
          >
            <el-button type="primary">选择文件</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传JSON或JSONL格式的数据文件
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="任务模板">
          <el-select v-model="createTaskForm.template" placeholder="请选择任务模板">
            <el-option
              v-for="template in availableTemplates"
              :key="template"
              :label="template"
              :value="template"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createTaskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createTask">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {
  Filter,
  Document,
  List,
  Monitor,
  Connection
} from '@element-plus/icons-vue'
import FormatUploader from '../components/FormatUploader.vue'

const router = useRouter()

// 状态
const activeMenu = ref('filter')
const tasks = ref([])
const availableFiles = ref([])
const availableTemplates = ref([])
const defaultAnnotationFields = ref(['是否缓刑', '罚金', '法定刑区间', '与宣告刑是否一致'])

// 表单数据
const filterForm = ref({
  selectedFiles: [],
  province: '',
  caseType: '',
  level: '',
  dateRange: [],
  caseReason: ''
})

const formatForm = ref({
  template: '',
  filename: ''
})

const aiReviewForm = ref({
  taskId: '',
  promptTemplate: ''
})

const trainingForm = ref({
  taskId: '',
  trainRatio: 0.8
})

// 创建任务相关
const createTaskDialogVisible = ref(false)
const createTaskForm = ref({
  name: '',
  description: '',
  data_file: null,
  template: 'template_default.json',
  config: []
})

// 方法
const handleMenuSelect = (key: string) => {
  activeMenu.value = key
}

const loadAvailableFiles = async () => {
  try {
    const response = await axios.get('/api/files')
    availableFiles.value = response.data.files
  } catch (error) {
    ElMessage.error('加载文件列表失败')
  }
}

const loadAvailableTemplates = async () => {
  try {
    const response = await axios.get('/api/templates')
    availableTemplates.value = response.data.templates
  } catch (error) {
    ElMessage.error('加载模板列表失败')
  }
}

const handleFilter = async () => {
  try {
    if (filterForm.value.selectedFiles.length === 0) {
      ElMessage.warning('请选择要过滤的文件')
      return
    }

    const filterConditions = {}
    if (filterForm.value.province) {
      filterConditions['province'] = filterForm.value.province
    }
    if (filterForm.value.caseType) {
      filterConditions['case_type'] = filterForm.value.caseType
    }
    if (filterForm.value.level) {
      filterConditions['level'] = filterForm.value.level
    }
    if (filterForm.value.dateRange && filterForm.value.dateRange.length === 2) {
      filterConditions['date_range'] = {
        start: filterForm.value.dateRange[0],
        end: filterForm.value.dateRange[1]
      }
    }
    if (filterForm.value.caseReason) {
      filterConditions['case_reason'] = filterForm.value.caseReason
    }

    const response = await axios.post('/api/filter', {
      file_names: filterForm.value.selectedFiles,
      filter_conditions: filterConditions
    })

    ElMessage.success(`过滤完成，共找到 ${response.data.document_count} 条数据`)
  } catch (error) {
    ElMessage.error('过滤失败')
  }
}

const handleFormat = async () => {
  try {
    const response = await axios.post('/api/format', formatForm.value)
    ElMessage.success('格式化完成')
  } catch (error) {
    ElMessage.error('格式化失败')
  }
}

const showCreateTaskDialog = () => {
  createTaskDialogVisible.value = true
}

const handleUploadSuccess = (response: any) => {
  console.log('上传成功响应:', response)  // 添加调试信息
  if (response.code === 200) {
    createTaskForm.value.data_file = response.data.file_id
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '文件上传失败')
  }
}

const handleUploadError = (error: any) => {
  console.error('上传错误:', error)  // 添加调试信息
  ElMessage.error('文件上传失败: ' + (error.response?.data?.detail || error.message || '未知错误'))
}

const beforeUpload = (file: File) => {
  console.log('准备上传文件:', file)  // 添加调试信息
  
  // 检查文件类型
  const isJSON = file.name.endsWith('.json')
  const isJSONL = file.name.endsWith('.jsonl')
  if (!isJSON && !isJSONL) {
    ElMessage.error('只能上传JSON或JSONL文件')
    return false
  }
  
  // 检查文件大小（限制为100MB）
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过100MB')
    return false
  }
  
  // 检查文件是否为空
  if (file.size === 0) {
    ElMessage.error('文件内容不能为空')
    return false
  }
  
  return true
}

const createTask = async () => {
  try {
    if (!createTaskForm.value.data_file) {
      ElMessage.warning('请先上传数据文件')
      return
    }

    const response = await axios.post('/api/tasks', createTaskForm.value)
    ElMessage.success('任务创建成功')
    createTaskDialogVisible.value = false
    loadTasks()
  } catch (error) {
    ElMessage.error('任务创建失败: ' + (error.response?.data?.detail || error.message))
  }
}

const handleEditTask = async (task: any) => {
  // 实现编辑任务的逻辑
}

const handleDeleteTask = async (task: any) => {
  try {
    await axios.delete(`/api/tasks/${task.id}`)
    ElMessage.success('任务删除成功')
    loadTasks()
  } catch (error) {
    ElMessage.error('任务删除失败')
  }
}

const startAnnotation = (task: any) => {
  router.push(`/annotator/${task.id}`)
}

const handleAIReview = async () => {
  try {
    const response = await axios.post(`/api/tasks/${aiReviewForm.value.taskId}/ai-review`, {
      prompt_template: aiReviewForm.value.promptTemplate
    })
    ElMessage.success('AI审查完成')
  } catch (error) {
    ElMessage.error('AI审查失败')
  }
}

const handleTraining = async () => {
  try {
    const response = await axios.post(`/api/tasks/${trainingForm.value.taskId}/prepare-training`, {
      train_ratio: trainingForm.value.trainRatio
    })
    ElMessage.success('训练数据准备完成')
  } catch (error) {
    ElMessage.error('训练数据准备失败')
  }
}

const handleMergeAnnotations = async (task: any) => {
  try {
    // 先检查任务是否已完成
    const completionResponse = await axios.get(`/api/tasks/${task.id}/completion`)
    if (!completionResponse.data.is_completed) {
      ElMessage.warning('任务尚未完成所有标注')
      return
    }

    // 执行合并
    const response = await axios.post(`/api/tasks/${task.id}/merge`)
    if (response.data.status === 'completed') {
      ElMessage.success('标注结果合并成功')
      // 重新加载任务列表以更新状态
      loadTasks()
    } else {
      ElMessage.error('合并失败')
    }
  } catch (error) {
    ElMessage.error('合并失败: ' + (error.response?.data?.detail || error.message))
  }
}

const loadTasks = async () => {
  try {
    const response = await axios.get('/api/tasks')
    tasks.value = response.data.tasks
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  }
}

// 添加字段
const addField = () => {
  createTaskForm.value.config.push({ path: '', type: '' })
}

// 删除字段
const removeField = (index: number) => {
  createTaskForm.value.config.splice(index, 1)
}

// 生命周期
onMounted(() => {
  loadTasks()
  loadAvailableFiles()
  loadAvailableTemplates()
})
</script>

<style scoped lang="scss">
.admin-container {
  height: 100vh;
  
  .el-aside {
    background-color: #304156;
    
    .el-menu {
      border-right: none;
    }
  }
  
  .el-main {
    padding: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}

.add-field {
  margin-top: 10px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>