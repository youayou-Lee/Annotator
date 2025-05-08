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
          <el-button type="success" @click="mergeAnnotations">重新合并标注</el-button>
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
                <pre class="json-content">{{ JSON.stringify(currentDocument, null, 2) }}</pre>
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
              <el-form :model="currentDocument" label-width="120px">
                <template v-for="field in generateAnnotationFields" :key="field.key">
                  <!-- 多值字段处理 -->
                  <template v-if="field.isMultiple">
                    <div class="multiple-field-container">
                      <div class="multiple-field-header">
                        <span>{{ field.label }}</span>
                        <el-tag size="small" type="info">多值字段</el-tag>
                      </div>
                      <div v-for="(path, index) in field.paths" :key="path" class="multiple-field-item">
                        <el-form-item :label="'值 ' + (index + 1)">
                          <template v-if="field.type === 'number'">
                            <el-input-number
                              :model-value="getFieldValue(currentDocument, path)"
                              @update:model-value="(val) => setFieldValue(currentDocument, path, val)"
                              :placeholder="`请输入${field.label}`"
                            />
                          </template>

                          <template v-else-if="field.type === 'boolean'">
                            <el-switch
                              :model-value="getFieldValue(currentDocument, path)"
                              @update:model-value="(val) => setFieldValue(currentDocument, path, val)"
                            />
                          </template>

                          <template v-else-if="field.type === 'array'">
                            <el-select
                              :model-value="getFieldValue(currentDocument, path)"
                              @update:model-value="(val) => setFieldValue(currentDocument, path, val)"
                              multiple
                              filterable
                              allow-create
                              default-first-option
                              style="width: 100%"
                            >
                              <el-option
                                v-for="item in getFieldValue(currentDocument, path) || []"
                                :key="item"
                                :label="item"
                                :value="item"
                              />
                            </el-select>
                          </template>

                          <template v-else>
                            <el-input
                              :model-value="getFieldValue(currentDocument, path)"
                              @update:model-value="(val) => setFieldValue(currentDocument, path, val)"
                              :type="getInputType(field.key, getFieldValue(currentDocument, path))"
                              :autosize="{ minRows: 2, maxRows: 4 }"
                              :placeholder="`请输入${field.label}`"
                            />
                          </template>
                        </el-form-item>
                      </div>
                    </div>
                  </template>
                  
                  <!-- 单值字段处理 -->
                  <template v-else>
                    <el-form-item :label="field.label">
                      <template v-if="field.type === 'number'">
                        <el-input-number
                          :model-value="getFieldValue(currentDocument, field.paths[0])"
                          @update:model-value="(val) => setFieldValue(currentDocument, field.paths[0], val)"
                          :placeholder="`请输入${field.label}`"
                        />
                      </template>

                      <template v-else-if="field.type === 'boolean'">
                        <el-switch
                          :model-value="getFieldValue(currentDocument, field.paths[0])"
                          @update:model-value="(val) => setFieldValue(currentDocument, field.paths[0], val)"
                        />
                      </template>

                      <template v-else-if="field.type === 'array'">
                        <el-select
                          :model-value="getFieldValue(currentDocument, field.paths[0])"
                          @update:model-value="(val) => setFieldValue(currentDocument, field.paths[0], val)"
                          multiple
                          filterable
                          allow-create
                          default-first-option
                          style="width: 100%"
                        >
                          <el-option
                            v-for="item in getFieldValue(currentDocument, field.paths[0]) || []"
                            :key="item"
                            :label="item"
                            :value="item"
                          />
                        </el-select>
                      </template>

                      <template v-else>
                        <el-input
                          :model-value="getFieldValue(currentDocument, field.paths[0])"
                          @update:model-value="(val) => setFieldValue(currentDocument, field.paths[0], val)"
                          :type="getInputType(field.key, getFieldValue(currentDocument, field.paths[0]))"
                          :autosize="{ minRows: 2, maxRows: 4 }"
                          :placeholder="`请输入${field.label}`"
                        />
                      </template>
                    </el-form-item>
                  </template>
                  
                  <span v-if="field.description" class="field-description">{{ field.description }}</span>
                </template>
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
import { ref, onMounted, computed } from 'vue'
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
const documentList = ref([])  // 新增：存储文档列表
const taskConfig = ref({
  fields: []
})  // 新增：存储任务配置

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
const loadDocumentList = async () => {
  try {
    const response = await axios.get(`/api/tasks/${taskId.value}/documents`)
    documentList.value = response.data.documents
    totalDocuments.value = documentList.value.length
  } catch (error) {
    ElMessage.error('加载文档列表失败')
  }
}

// 添加深度合并函数
const deepMerge = (target: any, source: any) => {
  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      target[key] = target[key] || {}
      deepMerge(target[key], source[key])
    } else {
      target[key] = source[key]
    }
  }
  return target
}

const loadDocument = async (page: number) => {
  try {
    if (!documentList.value || documentList.value.length === 0) {
      await loadDocumentList()
    }
    
    if (documentList.value && documentList.value.length > 0) {
      const currentDoc = documentList.value[page - 1]
      if (currentDoc) {
        // 确保每份文书都有一个id字段
        let documentId = currentDoc.id
        
        // 如果没有id字段，则尝试从其他字段生成一个id
        if (!documentId) {

          console.log('该Document没有ID！！！不合格，打回去重新搞')

        }
        
        // 根据任务配置初始化必要的字段结构
        if (taskConfig.value && taskConfig.value.initializeStructure) {
          for (const [key, defaultValue] of Object.entries(taskConfig.value.initializeStructure)) {
            if (!currentDoc[key] || (Array.isArray(currentDoc[key]) && currentDoc[key].length === 0)) {
              console.log(`初始化字段: ${key}`)
              currentDoc[key] = JSON.parse(JSON.stringify(defaultValue))
            }
          }
        }

        console.log('开始加载标注数据...')
        // 加载标注结果
        try {
          const annotationResponse = await axios.get(`/api/tasks/${taskId.value}/annotations/${documentId}`)
          console.log('标注响应:', annotationResponse.data)
          
          if (annotationResponse.data && annotationResponse.data.annotation && Object.keys(annotationResponse.data.annotation).length > 0) {
            console.log('找到标注数据，合并中...')
            // 创建原始文档的深拷贝
            const mergedDoc = JSON.parse(JSON.stringify(currentDoc))
            // 使用深度合并
            currentDocument.value = deepMerge(mergedDoc, annotationResponse.data.annotation)
            // 确保 ID 不会被覆盖
            currentDocument.value.id = documentId
            
            // 添加记录
            annotationHistory.value.unshift({
              timestamp: new Date().toLocaleString(),
              content: `已加载文档 [${documentId}] 的标注数据`,
              type: 'success'
            })
          } else {
            console.warn('未找到有效标注数据')
            // 如果没有标注结果或为空对象，使用原始文档
            currentDocument.value = JSON.parse(JSON.stringify(currentDoc))
            
            // 添加记录
            annotationHistory.value.unshift({
              timestamp: new Date().toLocaleString(),
              content: `未找到文档 [${documentId}] 的标注数据，使用原始文档`,
              type: 'warning'
            })
          }
        } catch (error) {
          console.warn('加载标注数据失败:', error)
          currentDocument.value = JSON.parse(JSON.stringify(currentDoc))
          
          // 添加记录
          annotationHistory.value.unshift({
            timestamp: new Date().toLocaleString(),
            content: `加载标注数据失败: ${error.message || '未知错误'}`,
            type: 'danger'
          })
        }
      }
    }
  } catch (error) {
    console.error('加载文档失败:', error)
    ElMessage.error('加载文档失败')
  }
}

const getFieldValue = (document: any, field: string) => {
  // Handle nested paths like "裁判详情.0.裁判结果.附加刑.罚金"
  const parts = field.split('.')
  let value = document
  for (const part of parts) {
    if (value === undefined) return undefined
    // Handle array index
    if (!isNaN(Number(part))) {
      value = value[Number(part)]
    } else {
      value = value[part]
    }
  }
  return value
}

const setFieldValue = (document: any, field: string, value: any) => {
  if (!document) return
  
  const parts = field.split('.')
  let current = document
  
  // 遍历路径
  for (let i = 0; i < parts.length - 1; i++) {
    const part = parts[i]
    if (!isNaN(Number(part))) {
      // 处理数组索引
      const index = Number(part)
      if (!Array.isArray(current)) {
        current = []
      }
      if (current[index] === undefined) {
        current[index] = {}
      }
      current = current[index]
    } else {
      if (!current[part]) {
        current[part] = {}
      }
      current = current[part]
    }
  }

  const lastPart = parts[parts.length - 1]
  const oldValue = current[lastPart]
  
  // 只有值确实改变了才更新
  if (value !== oldValue) {
    // 根据字段类型设置值
    if (['罚金', '管制', '拘役', '有期徒刑'].includes(lastPart)) {
      current[lastPart] = value === '' ? 0 : Number(value)
    } else if (typeof value === 'boolean') {
      current[lastPart] = value
    } else {
      current[lastPart] = value
    }

    // 添加修改记录到历史
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: `修改字段 "${field}" 的值：${oldValue} -> ${value}`,
      type: 'info'
    })

    // 实时保存到后端
    saveAnnotation()
  }
}

// 获取当前文档中某个字段的所有路径
const findPathsInDocument = (document: any, key: string, currentPath: string = ""): string[] => {
  const paths: string[] = []
  
  if (!document) return paths

  if (typeof document === 'object') {
    for (const [k, v] of Object.entries(document)) {
      const newPath = currentPath ? `${currentPath}.${k}` : k
      if (k === key) {
        paths.push(newPath)
      }
      if (Array.isArray(v)) {
        v.forEach((item, index) => {
          // 使用点号表示法处理数组索引，而不是方括号
          const arrayPath = `${newPath}.${index}`
          paths.push(...findPathsInDocument(item, key, arrayPath))
        })
      } else if (typeof v === 'object' && v !== null) {
        paths.push(...findPathsInDocument(v, key, newPath))
      }
    }
  }
  
  return paths
}

// 生成标注字段
const generateAnnotationFields = computed(() => {
  if (!taskConfig.value?.fields || !currentDocument.value) return []
  
  return taskConfig.value.fields.map((field) => {
    // 在当前文档中查找这个字段的所有路径
    const paths = findPathsInDocument(currentDocument.value, field.key)
    
    return {
      key: field.key,
      label: field.key,
      type: field.type,
      description: field.description,
      isMultiple: paths.length > 1,
      paths: paths.length > 0 ? paths : [field.key] // 如果找不到路径，使用默认路径
    }
  })
})

const saveAnnotation = async () => {
  try {
    const documentId = currentDocument.value?.id || currentDocument.value?.s5
    if (!documentId) {
      throw new Error('文档ID不存在')
    }
    
    // 创建标注对象
    const annotation = {}
    
    // 获取当前文档中的实际字段路径
    const currentFields = generateAnnotationFields.value
    
    for (const field of currentFields) {
      const paths = field.paths || []
      
      // 确保路径有效
      if (paths.length === 0) continue

      // 处理每个路径
      paths.forEach(path => {
        const value = getFieldValue(currentDocument.value, path)
        if (value !== undefined) {
          // 使用点号分割路径并创建嵌套对象
          let target = annotation
          const parts = path.split('.')
          
          for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i]
            // 处理数组索引
            if (!isNaN(Number(part))) {
              const index = Number(part)
              // 确保父级是数组
              if (!Array.isArray(target)) {
                target = []
              }
              // 初始化数组到所需长度
              while (target.length <= index) {
                target.push({})
              }
              if (!target[index]) {
                target[index] = {}
              }
              target = target[index]
            } else {
              // 处理对象属性
              if (!target[part] || typeof target[part] !== 'object') {
                target[part] = {}
              }
              target = target[part]
            }
          }
          
          // 设置最终值
          const lastPart = parts[parts.length - 1]
          if (field.type === 'number') {
            target[lastPart] = value === '' ? 0 : Number(value)
          } else {
            target[lastPart] = value
          }
        }
      })
    }

    // 发送到后端
    await axios.post(
      `/api/tasks/${taskId.value}/annotations/${documentId}`, 
      annotation
    )

    ElMessage.success('保存成功')
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: `已保存第 ${currentPage.value} 页的标注`,
      type: 'success'
    })
  } catch (error) {
    console.error('保存标注失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: `保存第 ${currentPage.value} 页标注失败`,
      type: 'danger'
    })
  }
}

// 合并标注
const mergeAnnotations = async () => {
  try {
    // 先保存当前文档的标注，确保最新的更改被包含
    await saveAnnotation()
    
    // 调用后端合并接口
    const response = await axios.post(`/api/tasks/${taskId.value}/merge-annotations`)
    
    if (response.data.status === 'success') {
      ElMessage.success('合并标注成功')
      annotationHistory.value.unshift({
        timestamp: new Date().toLocaleString(),
        content: '标注已成功合并并保存到merged_data目录',
        type: 'success'
      })
    } else {
      throw new Error(response.data.message || '合并操作返回未知状态')
    }
  } catch (error) {
    console.error('合并标注失败:', error)
    ElMessage.error('合并标注失败: ' + (error.response?.data?.detail || error.message))
    annotationHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      content: '合并标注失败',
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

// 获取任务配置
const loadTaskConfig = async () => {
  try {
    const response = await axios.get(`/api/tasks/${taskId.value}/config`)
    if (!response.data?.config?.fields) {
      throw new Error('配置数据格式错误')
    }
    taskConfig.value = {
      fields: response.data.config.fields.map(field => ({
        key: field.key,
        name: field.key,
        type: field.type,
        description: field.description || ''
      })),
      beMarked: response.data.config.beMarked || []
    }
  } catch (error) {
    console.error('加载任务配置失败:', error)
    ElMessage.error('加载任务配置失败：' + (error.response?.data?.detail || error.message))
  }
}

// 判断字段是否可编辑
const isFieldEditable = (field: string): boolean => {
  return taskConfig.value?.beMarked?.includes(field) ?? true
}

// 获取输入框类型
const getInputType = (key: string, value: any): string => {
  if (typeof value === 'string' && value.length > 50) {
    return 'textarea'
  }
  return 'text'
}

// 生命周期
onMounted(async () => {
  // 从路由参数获取任务ID
  taskId.value = route.params.taskId as string
  if (!taskId.value) {
    ElMessage.error('未找到任务ID')
    router.push('/admin')
    return
  }
  
  await loadTaskConfig()
  await loadDocumentList()
  await loadDocument(1)
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
    .json-content {
      white-space: pre-wrap;
      word-wrap: break-word;
      background-color: #f5f7fa;
      padding: 15px;
      border-radius: 4px;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
      font-size: 14px;
      line-height: 1.5;
      border: 1px solid #e4e7ed;
    }
  }
  
  .history-card {
    height: 300px;
  }

  .multiple-field-container {
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 20px;
    background-color: #f8f9fb;

    .multiple-field-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e4e7ed;

      span {
        font-weight: bold;
        font-size: 14px;
      }
    }

    .multiple-field-item {
      padding: 10px;
      margin-bottom: 10px;
      border-radius: 4px;
      background-color: #fff;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

      &:last-child {
        margin-bottom: 0;
      }
    }
  }

  .field-description {
    display: block;
    font-size: 12px;
    color: #909399;
    margin: 5px 0 15px 120px;
  }
}
</style>