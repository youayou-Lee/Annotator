# PowerShell 测试数据生成脚本

# 确保测试数据目录存在
$testDataDir = Join-Path -Path (Get-Location) -ChildPath "test_data"
if (-not (Test-Path -Path $testDataDir)) {
    New-Item -Path $testDataDir -ItemType Directory -Force | Out-Null
    Write-Host "已创建测试数据目录: $testDataDir" -ForegroundColor Green
}

# 生成JSON测试文件
$validJsonPath = Join-Path -Path $testDataDir -ChildPath "valid-document.json"
$validJson = @{
    name = "测试文档"
    description = "这是一个测试文档"
    date = "2023-05-15"
    author = "测试用户"
    version = "1.0.0"
    fields = @(
        @{ name = "姓名"; type = "string"; required = $true }
        @{ name = "年龄"; type = "number"; min = 0; max = 120 }
        @{ name = "地址"; type = "string"; required = $false }
        @{ name = "电话"; type = "string"; pattern = "^\d{11}$" }
    )
    items = @(
        @{ id = 1; value = "测试项目1" }
        @{ id = 2; value = "测试项目2" }
        @{ id = 3; value = "测试项目3" }
    )
}

$validJsonContent = ConvertTo-Json -InputObject $validJson -Depth 4
Set-Content -Path $validJsonPath -Value $validJsonContent
Write-Host "已生成有效的JSON文件: $validJsonPath" -ForegroundColor Green

# 生成无效的JSON文件
$invalidJsonPath = Join-Path -Path $testDataDir -ChildPath "invalid-document.json"
$invalidJsonContent = @"
{
    "name": "测试文档",
    "description": "这是一个格式错误的JSON",
    "date": 2023-05-15,
    "fields": [
      { "name": "姓名", "type": "string", required: true },
      { "name": "年龄", "type": "number", "min": 0, "max": 120 },
    ]
}
"@
Set-Content -Path $invalidJsonPath -Value $invalidJsonContent
Write-Host "已生成无效的JSON文件: $invalidJsonPath" -ForegroundColor Green

# 生成有效的CSV测试文件
$validCsvPath = Join-Path -Path $testDataDir -ChildPath "valid-document.csv"
$validCsvContent = @"
姓名,年龄,地址,电话
张三,28,北京市海淀区,13800138000
李四,35,上海市浦东新区,13900139000
王五,42,广州市天河区,13700137000
"@
Set-Content -Path $validCsvPath -Value $validCsvContent
Write-Host "已生成有效的CSV文件: $validCsvPath" -ForegroundColor Green

# 生成无效的CSV测试文件
$invalidCsvPath = Join-Path -Path $testDataDir -ChildPath "invalid-document.csv"
$invalidCsvContent = @"
姓名,年龄,地址
张三,28,北京市海淀区
李四,,上海市浦东新区
王五,四十二,广州市天河区
"@
Set-Content -Path $invalidCsvPath -Value $invalidCsvContent
Write-Host "已生成无效的CSV文件: $invalidCsvPath" -ForegroundColor Green

# 生成Python校验文件
$pyFilePath = Join-Path -Path $testDataDir -ChildPath "validation_model.py"
$pyFileContent = @"
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class Address(BaseModel):
    city: str
    street: str
    zipcode: str = Field(..., pattern=r'^\d{6}$')

class Person(BaseModel):
    name: str
    age: int = Field(..., gt=0, lt=120)
    birth_date: date
    address: Optional[Address] = None
    phone: str = Field(..., pattern=r'^\d{11}$')
    
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
"@
Set-Content -Path $pyFilePath -Value $pyFileContent
Write-Host "已生成Python校验文件: $pyFilePath" -ForegroundColor Green

# 生成普通文本文件
$textFilePath = Join-Path -Path $testDataDir -ChildPath "document.txt"
$textFileContent = @"
这是一个普通的文本文件
用于测试上传不支持的文件格式
系统应该拒绝这种格式的文件
"@
Set-Content -Path $textFilePath -Value $textFileContent
Write-Host "已生成普通文本文件: $textFilePath" -ForegroundColor Green

Write-Host "所有测试文件生成完成！" -ForegroundColor Green 