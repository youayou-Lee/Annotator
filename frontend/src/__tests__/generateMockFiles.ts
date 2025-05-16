import * as fs from 'fs';
import * as path from 'path';

// 测试文件存储目录
const testFilesDir = path.resolve(__dirname, '../../../test_data');

// 确保测试目录存在
if (!fs.existsSync(testFilesDir)) {
  fs.mkdirSync(testFilesDir, { recursive: true });
}

// 生成有效的JSON测试文件
function generateValidJsonFile() {
  const validData = {
    name: '测试文档',
    description: '这是一个测试文档',
    date: '2023-05-15',
    author: '测试用户',
    version: '1.0.0',
    fields: [
      { name: '姓名', type: 'string', required: true },
      { name: '年龄', type: 'number', min: 0, max: 120 },
      { name: '地址', type: 'string', required: false },
      { name: '电话', type: 'string', pattern: '^\\d{11}$' },
    ],
    items: [
      { id: 1, value: '测试项目1' },
      { id: 2, value: '测试项目2' },
      { id: 3, value: '测试项目3' },
    ]
  };

  const filePath = path.join(testFilesDir, 'valid-document.json');
  fs.writeFileSync(filePath, JSON.stringify(validData, null, 2));
  console.log(`已生成有效的JSON文件: ${filePath}`);
}

// 生成无效的JSON测试文件 (格式错误)
function generateInvalidJsonFile() {
  const invalidJson = `{
    "name": "测试文档",
    "description": "这是一个格式错误的JSON",
    "date": 2023-05-15,
    "fields": [
      { "name": "姓名", "type": "string", required: true },
      { "name": "年龄", "type": "number", "min": 0, "max": 120 },
    ]
  }`;

  const filePath = path.join(testFilesDir, 'invalid-document.json');
  fs.writeFileSync(filePath, invalidJson);
  console.log(`已生成无效的JSON文件: ${filePath}`);
}

// 生成有效的CSV测试文件
function generateValidCsvFile() {
  const csvContent = `姓名,年龄,地址,电话
张三,28,北京市海淀区,13800138000
李四,35,上海市浦东新区,13900139000
王五,42,广州市天河区,13700137000`;

  const filePath = path.join(testFilesDir, 'valid-document.csv');
  fs.writeFileSync(filePath, csvContent);
  console.log(`已生成有效的CSV文件: ${filePath}`);
}

// 生成无效的CSV测试文件 (缺少列)
function generateInvalidCsvFile() {
  const csvContent = `姓名,年龄,地址
张三,28,北京市海淀区
李四,,上海市浦东新区
王五,四十二,广州市天河区`;

  const filePath = path.join(testFilesDir, 'invalid-document.csv');
  fs.writeFileSync(filePath, csvContent);
  console.log(`已生成无效的CSV文件: ${filePath}`);
}

// 生成有效的Python校验文件
function generateValidPyFile() {
  const pyContent = `
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class Address(BaseModel):
    city: str
    street: str
    zipcode: str = Field(..., pattern=r'^\\d{6}$')

class Person(BaseModel):
    name: str
    age: int = Field(..., gt=0, lt=120)
    birth_date: date
    address: Optional[Address] = None
    phone: str = Field(..., pattern=r'^\\d{11}$')
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('姓名不能为空')
        return v

class DocumentModel(BaseModel):
    title: str
    created_at: date
    updated_at: Optional[date] = None
    persons: List[Person]
    
    class Config:
        schema_extra = {
            "example": {
                "title": "人员信息表",
                "created_at": "2023-05-15",
                "persons": [
                    {
                        "name": "张三",
                        "age": 28,
                        "birth_date": "1995-03-12",
                        "phone": "13800138000",
                        "address": {
                            "city": "北京",
                            "street": "海淀区xx街道",
                            "zipcode": "100000"
                        }
                    }
                ]
            }
        }
`;

  const filePath = path.join(testFilesDir, 'validation_model.py');
  fs.writeFileSync(filePath, pyContent);
  console.log(`已生成有效的Python校验文件: ${filePath}`);
}

// 生成一个普通文本文件 (不支持的格式)
function generateTextFile() {
  const textContent = `这是一个普通的文本文件
用于测试上传不支持的文件格式
系统应该拒绝这种格式的文件`;

  const filePath = path.join(testFilesDir, 'document.txt');
  fs.writeFileSync(filePath, textContent);
  console.log(`已生成普通文本文件: ${filePath}`);
}

// 生成所有测试文件
function generateAllTestFiles() {
  console.log('开始生成测试文件...');
  generateValidJsonFile();
  generateInvalidJsonFile();
  generateValidCsvFile();
  generateInvalidCsvFile();
  generateValidPyFile();
  generateTextFile();
  console.log('所有测试文件生成完成！');
}

// 执行生成
generateAllTestFiles();

// 导出函数以供需要时调用
export {
  generateValidJsonFile,
  generateInvalidJsonFile,
  generateValidCsvFile,
  generateInvalidCsvFile,
  generateValidPyFile,
  generateTextFile,
  generateAllTestFiles,
}; 