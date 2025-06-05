/**
 * 表单数据管理器
 * 负责处理模板字段与文档内容的映射、表单数据的初始化和更新
 */

import { TemplateField } from '../components/DynamicFormGenerator'

// 辅助函数：获取嵌套对象的值
export const getNestedValue = (obj: any, path: string): any => {
  if (!obj || !path) return undefined
  
  let current = obj
  
  // 特殊处理：如果文档结构是 {items: [...], type: 'array'}，则从items[0]开始
  if (obj.items && Array.isArray(obj.items) && obj.items.length > 0 && obj.type === 'array') {
    current = obj.items[0]
  }
  
  // 处理包含数组索引的路径 如: 相似罪名[].罪名
  if (path.includes('[]')) {
    const parts = path.split('[]')
    let arrayPath = parts[0] // 相似罪名
    let remainingPath = parts[1] // .罪名
    
    // 获取到数组
    const arrayKeys = arrayPath.split('.')
    for (const key of arrayKeys) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key]
      } else {
        return undefined
      }
    }
    
    // 如果是数组，取第一个元素
    if (Array.isArray(current) && current.length > 0) {
      current = current[0]
      
      // 处理剩余路径（去掉开头的点号）
      if (remainingPath && remainingPath.startsWith('.')) {
        remainingPath = remainingPath.substring(1)
      }
      
      if (remainingPath) {
        // 递归处理剩余路径（可能还有嵌套数组）
        return getNestedValue(current, remainingPath)
      } else {
        return current
      }
    } else {
      return undefined
    }
  } else {
    // 普通路径处理
    const keys = path.split('.')
    
    for (const key of keys) {
      if (current === null || current === undefined) {
        return undefined
      }
      current = current[key]
    }
    
    return current
  }
}

// 辅助函数：设置嵌套对象的值
export const setNestedValue = (obj: any, path: string, value: any): any => {
  if (!path) return obj
  
  // 深拷贝对象
  const result = { ...obj }
  
  // 处理包含数组索引的路径 如: 相似罪名[].罪名
  if (path.includes('[]')) {
    const parts = path.split('[]')
    let arrayPath = parts[0] // 相似罪名
    let remainingPath = parts[1] // .罪名
    
    // 获取到数组的父对象
    const arrayKeys = arrayPath.split('.')
    let arrayParent = result
    
    // 导航到数组所在的父对象
    for (let i = 0; i < arrayKeys.length - 1; i++) {
      const key = arrayKeys[i]
      if (!arrayParent[key] || typeof arrayParent[key] !== 'object') {
        arrayParent[key] = {}
      } else {
        arrayParent[key] = { ...arrayParent[key] }
      }
      arrayParent = arrayParent[key]
    }
    
    // 获取数组字段的键
    const arrayKey = arrayKeys[arrayKeys.length - 1]
    
    // 确保数组存在
    if (!Array.isArray(arrayParent[arrayKey])) {
      arrayParent[arrayKey] = []
    } else {
      arrayParent[arrayKey] = [...arrayParent[arrayKey]]
    }
    
    // 如果数组为空，创建第一个元素
    if (arrayParent[arrayKey].length === 0) {
      arrayParent[arrayKey].push({})
    }
    
    // 处理剩余路径（去掉开头的点号）
    if (remainingPath && remainingPath.startsWith('.')) {
      remainingPath = remainingPath.substring(1)
    }
    
    if (remainingPath) {
      // 递归处理剩余路径，更新数组中第一个元素
      arrayParent[arrayKey][0] = setNestedValue(arrayParent[arrayKey][0], remainingPath, value)
    } else {
      // 如果没有剩余路径，直接设置整个数组元素
      arrayParent[arrayKey][0] = value
    }
    
    return result
  } else {
    // 普通路径处理
    const keys = path.split('.')
    let current = result
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i]
      if (current[key] === undefined || current[key] === null) {
        current[key] = {}
      } else {
        current[key] = { ...current[key] }
      }
      current = current[key]
    }
    
    current[keys[keys.length - 1]] = value
    return result
  }
}

// 辅助函数：删除嵌套对象的值
export const deleteNestedValue = (obj: any, path: string): any => {
  if (!path) return obj
  
  const keys = path.split('.')
  const result = { ...obj }
  let current = result
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    if (current[key] === undefined || current[key] === null) {
      return result // 路径不存在，直接返回
    }
    current[key] = { ...current[key] }
    current = current[key]
  }
  
  delete current[keys[keys.length - 1]]
  return result
}

// 辅助函数：检查两个对象是否深度相等
export const deepEqual = (obj1: any, obj2: any): boolean => {
  if (obj1 === obj2) return true
  
  if (obj1 == null || obj2 == null) return obj1 === obj2
  
  if (typeof obj1 !== typeof obj2) return false
  
  if (typeof obj1 !== 'object') return obj1 === obj2
  
  if (Array.isArray(obj1) !== Array.isArray(obj2)) return false
  
  if (Array.isArray(obj1)) {
    if (obj1.length !== obj2.length) return false
    for (let i = 0; i < obj1.length; i++) {
      if (!deepEqual(obj1[i], obj2[i])) return false
    }
    return true
  }
  
  const keys1 = Object.keys(obj1)
  const keys2 = Object.keys(obj2)
  
  if (keys1.length !== keys2.length) return false
  
  for (const key of keys1) {
    if (!keys2.includes(key)) return false
    if (!deepEqual(obj1[key], obj2[key])) return false
  }
  
  return true
}

export class FormDataManager {
  private templateFields: TemplateField[]
  private documentContent: Record<string, any>
  private annotatedContent: Record<string, any>
  
  constructor(
    templateFields: TemplateField[],
    documentContent: Record<string, any>,
    annotatedContent: Record<string, any> = {}
  ) {
    this.templateFields = templateFields
    this.documentContent = documentContent
    this.annotatedContent = annotatedContent
  }
  
  /**
   * 初始化表单数据
   * 将原始文档内容按模板字段映射到表单
   */
  initializeFormData(): Record<string, any> {
    const formData: Record<string, any> = { ...this.annotatedContent }
    
    // 遍历模板字段，将原始文档内容映射到表单
    this.templateFields.forEach(field => {
      const fieldPath = field.path
      const originalValue = getNestedValue(this.documentContent, fieldPath)
      const annotatedValue = getNestedValue(this.annotatedContent, fieldPath)
      
      // 如果标注内容中没有该字段值，则使用原始文档的值
      if (annotatedValue === undefined && originalValue !== undefined) {
        if (fieldPath.includes('.')) {
          // 嵌套字段
          setNestedValue(formData, fieldPath, originalValue)
        } else {
          // 简单字段
          formData[fieldPath] = originalValue
        }
      }
    })
    
    return formData
  }
  
  /**
   * 更新表单数据
   * 处理单个字段的值变化
   */
  updateFieldValue(
    currentData: Record<string, any>,
    fieldPath: string,
    value: any
  ): Record<string, any> {
    if (fieldPath.includes('.')) {
      // 嵌套字段
      return setNestedValue(currentData, fieldPath, value)
    } else {
      // 简单字段
      return {
        ...currentData,
        [fieldPath]: value
      }
    }
  }
  
  /**
   * 批量更新表单数据
   * 处理多个字段的值变化
   */
  updateMultipleFields(
    currentData: Record<string, any>,
    changes: Record<string, any>
  ): Record<string, any> {
    let updatedData = { ...currentData }
    
    Object.keys(changes).forEach(fieldPath => {
      updatedData = this.updateFieldValue(updatedData, fieldPath, changes[fieldPath])
    })
    
    return updatedData
  }
  
  /**
   * 验证表单数据
   * 检查必填字段是否已填写
   */
  validateFormData(formData: Record<string, any>): {
    valid: boolean
    errors: Record<string, string>
  } {
    const errors: Record<string, string> = {}
    
    this.templateFields.forEach(field => {
      if (field.required) {
        const value = getNestedValue(formData, field.path)
        if (value === undefined || value === null || value === '') {
          errors[field.path] = `${field.description || field.path}是必填项`
        }
      }
      
      // 检查字段约束
      if (field.constraints) {
        const value = getNestedValue(formData, field.path)
        if (value !== undefined && value !== null) {
          // 字符串长度约束
          if (field.constraints.max_length && typeof value === 'string') {
            if (value.length > field.constraints.max_length) {
              errors[field.path] = `${field.description || field.path}长度不能超过${field.constraints.max_length}个字符`
            }
          }
          
          if (field.constraints.min_length && typeof value === 'string') {
            if (value.length < field.constraints.min_length) {
              errors[field.path] = `${field.description || field.path}长度不能少于${field.constraints.min_length}个字符`
            }
          }
          
          // 数值范围约束
          if (field.constraints.le && typeof value === 'number') {
            if (value > field.constraints.le) {
              errors[field.path] = `${field.description || field.path}不能大于${field.constraints.le}`
            }
          }
          
          if (field.constraints.ge && typeof value === 'number') {
            if (value < field.constraints.ge) {
              errors[field.path] = `${field.description || field.path}不能小于${field.constraints.ge}`
            }
          }
        }
      }
    })
    
    return {
      valid: Object.keys(errors).length === 0,
      errors
    }
  }
  
  /**
   * 获取字段的原始值
   */
  getOriginalValue(fieldPath: string): any {
    return getNestedValue(this.documentContent, fieldPath)
  }
  
  /**
   * 获取字段的已标注值
   */
  getAnnotatedValue(fieldPath: string): any {
    return getNestedValue(this.annotatedContent, fieldPath)
  }
  
  /**
   * 检查字段是否已修改
   */
  isFieldModified(fieldPath: string, currentValue: any): boolean {
    const originalValue = this.getOriginalValue(fieldPath)
    return !deepEqual(originalValue, currentValue)
  }
  
  /**
   * 获取所有已修改的字段
   */
  getModifiedFields(formData: Record<string, any>): string[] {
    const modifiedFields: string[] = []
    
    this.templateFields.forEach(field => {
      const currentValue = getNestedValue(formData, field.path)
      if (this.isFieldModified(field.path, currentValue)) {
        modifiedFields.push(field.path)
      }
    })
    
    return modifiedFields
  }
  
  /**
   * 重置字段到原始值
   */
  resetFieldToOriginal(
    currentData: Record<string, any>,
    fieldPath: string
  ): Record<string, any> {
    const originalValue = this.getOriginalValue(fieldPath)
    if (originalValue !== undefined) {
      return this.updateFieldValue(currentData, fieldPath, originalValue)
    } else {
      // 如果原始值不存在，删除该字段
      return deleteNestedValue(currentData, fieldPath)
    }
  }
  
  /**
   * 重置所有字段到原始值
   */
  resetAllFieldsToOriginal(): Record<string, any> {
    return this.initializeFormData()
  }
  
  /**
   * 获取表单数据的统计信息
   */
  getFormDataStats(formData: Record<string, any>): {
    totalFields: number
    filledFields: number
    modifiedFields: number
    completionPercentage: number
  } {
    const totalFields = this.templateFields.length
    let filledFields = 0
    let modifiedFields = 0
    
    this.templateFields.forEach(field => {
      const value = getNestedValue(formData, field.path)
      if (value !== undefined && value !== null && value !== '') {
        filledFields++
      }
      
      if (this.isFieldModified(field.path, value)) {
        modifiedFields++
      }
    })
    
    return {
      totalFields,
      filledFields,
      modifiedFields,
      completionPercentage: totalFields > 0 ? (filledFields / totalFields) * 100 : 0
    }
  }
  
  /**
   * 更新模板字段
   */
  updateTemplateFields(templateFields: TemplateField[]): void {
    this.templateFields = templateFields
  }
  
  /**
   * 更新文档内容
   */
  updateDocumentContent(documentContent: Record<string, any>): void {
    this.documentContent = documentContent
  }
  
  /**
   * 更新已标注内容
   */
  updateAnnotatedContent(annotatedContent: Record<string, any>): void {
    this.annotatedContent = annotatedContent
  }
}