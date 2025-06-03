/**
 * 表单数据管理器
 * 负责处理模板字段与文档内容的映射、表单数据的初始化和更新
 */

import { TemplateField } from '../components/DynamicFormGenerator'

// 辅助函数：获取嵌套对象的值
export const getNestedValue = (obj: any, path: string): any => {
  if (!obj || !path) return undefined
  
  const keys = path.split('.')
  let current = obj
  
  for (const key of keys) {
    if (current === null || current === undefined) {
      return undefined
    }
    current = current[key]
  }
  
  return current
}

// 辅助函数：设置嵌套对象的值
export const setNestedValue = (obj: any, path: string, value: any): any => {
  if (!path) return obj
  
  const keys = path.split('.')
  const result = { ...obj }
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