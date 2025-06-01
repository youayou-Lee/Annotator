from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date

class ContractType(str, Enum):
    SOFTWARE_DEVELOPMENT = "软件开发合同"
    PROCUREMENT = "采购合同"
    SERVICE = "服务合同"
    CONSULTING = "咨询合同"
    LEASE = "租赁合同"
    EMPLOYMENT = "劳动合同"
    PARTNERSHIP = "合作协议"
    OTHER = "其他"

class RiskLevel(str, Enum):
    LOW = "低"
    MEDIUM = "中等"
    HIGH = "高"
    CRITICAL = "极高"

class ApprovalStatus(str, Enum):
    PENDING = "待审批"
    APPROVED = "已审批"
    REJECTED = "已拒绝"
    EXPIRED = "已过期"

class Currency(str, Enum):
    CNY = "CNY"
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"

class PartyType(str, Enum):
    PARTY_A = "甲方"
    PARTY_B = "乙方"
    PARTY_C = "丙方"

class PartyRole(str, Enum):
    PRINCIPAL = "委托方"
    CONTRACTOR = "承接方"
    PURCHASER = "采购方"
    SUPPLIER = "供应方"
    SERVICE_PROVIDER = "服务方"
    OTHER = "其他"

class ClauseType(str, Enum):
    CONFIDENTIALITY = "保密条款"
    INTELLECTUAL_PROPERTY = "知识产权条款"
    BREACH_LIABILITY = "违约责任条款"
    DISPUTE_RESOLUTION = "争议解决条款"
    QUALITY_ASSURANCE = "质量保证条款"
    AFTER_SALES_SERVICE = "售后服务条款"
    SERVICE_LEVEL_AGREEMENT = "服务水平协议"
    DATA_SECURITY = "数据安全条款"

class PartyInfo(BaseModel):
    party_name: str = Field(description="当事方名称", example="北京科技有限公司")
    party_type: PartyType = Field(
        description="当事方类型",
        example=PartyType.PARTY_A
    )
    party_role: PartyRole = Field(
        description="当事方角色",
        example=PartyRole.PRINCIPAL
    )
    legal_representative: Optional[str] = Field(
        description="法定代表人",
        default="",
        example="张三"
    )
    contact_person: Optional[str] = Field(
        description="联系人",
        default="",
        example="李经理"
    )
    contact_phone: Optional[str] = Field(
        description="联系电话",
        default="",
        example="010-12345678"
    )
    address: Optional[str] = Field(
        description="地址",
        default="",
        example="北京市海淀区中关村大街1号"
    )

class PaymentTerm(BaseModel):
    payment_stage: str = Field(description="付款阶段", example="合同签署")
    payment_percentage: float = Field(
        description="付款比例(%)",
        ge=0.0,
        le=100.0,
        example=30.0
    )
    payment_amount: float = Field(description="付款金额", ge=0, example=150000)
    due_date: Optional[str] = Field(
        description="付款期限",
        default="",
        example="2024-01-15"
    )
    payment_condition: Optional[str] = Field(
        description="付款条件",
        default="",
        example="收到发票后30天内"
    )

class ContractClause(BaseModel):
    clause_type: ClauseType = Field(
        description="条款类型",
        example=ClauseType.CONFIDENTIALITY
    )
    clause_content: str = Field(
        description="条款内容摘要",
        ui_widget="textarea",
        example="双方应对在合同履行过程中获得的商业秘密承担保密义务"
    )
    risk_assessment: RiskLevel = Field(
        description="风险评估",
        example=RiskLevel.MEDIUM
    )
    compliance_check: bool = Field(
        description="合规性检查通过",
        example=True
    )

class AnnotationSchema:
    schema_name = "合同文档标注模板"
    version = "1.0.0"
    description = "用于合同文档关键信息提取和风险评估的标注模板，支持多种合同类型的结构化分析"
    
    class Fields(BaseModel):
        # 合同基本信息
        contract_title: str = Field(
            description="合同标题",
            min_length=1,
            max_length=200,
            example="智能客服系统开发合同"
        )
        
        contract_number: str = Field(
            description="合同编号",
            min_length=1,
            max_length=50,
            example="SD-2024-001"
        )
        
        contract_type: ContractType = Field(
            description="合同类型",
            example=ContractType.SOFTWARE_DEVELOPMENT
        )
        
        # 当事方信息
        contracting_parties: List[PartyInfo] = Field(
            description="合同当事方信息",
            min_items=2,
            max_items=5,
            example=[{
                "party_name": "北京科技有限公司",
                "party_type": "甲方",
                "party_role": "委托方",
                "legal_representative": "",
                "contact_person": "李经理",
                "contact_phone": "010-12345678",
                "address": "北京市海淀区中关村大街1号"
            }]
        )
        
        # 合同金额和支付条款
        total_contract_amount: float = Field(
            description="合同总金额",
            ge=0,
            example=500000.0
        )
        
        contract_currency: Currency = Field(
            description="合同币种",
            example=Currency.CNY
        )
        
        payment_terms: List[PaymentTerm] = Field(
            description="付款条款",
            default=[],
            example=[{
                "payment_stage": "合同签署",
                "payment_percentage": 30.0,
                "payment_amount": 150000,
                "due_date": "2024-01-15",
                "payment_condition": "合同生效后7个工作日内"
            }]
        )
        
        # 合同履行信息
        project_scope: str = Field(
            description="项目范围/标的物描述",
            ui_widget="textarea",
            min_length=10,
            example="开发一套智能客服系统，包括自然语言处理、知识库管理、多渠道接入等功能模块"
        )
        
        deliverables: List[str] = Field(
            description="交付物清单",
            default=[],
            example=["需求分析文档", "系统设计文档", "源代码", "部署文档"]
        )
        
        contract_start_date: Optional[str] = Field(
            description="合同开始日期",
            ui_widget="date-picker",
            default="",
            example="2024-01-01"
        )
        
        contract_end_date: Optional[str] = Field(
            description="合同结束日期",
            ui_widget="date-picker",
            default="",
            example="2024-05-31"
        )
        
        contract_duration: Optional[float] = Field(
            description="合同期限(月)",
            ge=0,
            default=None,
            example=5.0
        )
        
        # 重要条款分析
        key_clauses: List[ContractClause] = Field(
            description="重要条款分析",
            default=[],
            example=[{
                "clause_type": "保密条款",
                "clause_content": "双方应对在合同履行过程中获得的商业秘密承担保密义务",
                "risk_assessment": "中等",
                "compliance_check": True
            }]
        )
        
        # 风险评估
        overall_risk_level: RiskLevel = Field(
            description="整体风险等级",
            example=RiskLevel.MEDIUM
        )
        
        risk_factors: List[str] = Field(
            description="风险因素识别",
            default=[],
            example=["技术实现难度较高", "项目周期紧张", "付款条件较为严格"]
        )
        
        mitigation_measures: List[str] = Field(
            description="风险缓解措施",
            default=[],
            example=["增加技术评审环节", "制定详细项目计划", "建立定期沟通机制"]
        )
        
        # 合规性检查
        legal_compliance: bool = Field(
            description="法律合规性检查通过",
            example=True
        )
        
        approval_status: ApprovalStatus = Field(
            description="审批状态",
            example=ApprovalStatus.PENDING
        )
        
        approval_comments: Optional[str] = Field(
            description="审批意见",
            ui_widget="textarea",
            default="",
            example="合同条款清晰，风险可控，建议批准。"
        )
        
        # 特殊条款标识
        contains_penalty_clause: bool = Field(
            description="是否包含违约金条款",
            example=True
        )
        
        contains_ip_clause: bool = Field(
            description="是否包含知识产权条款",
            example=True
        )
        
        contains_confidentiality_clause: bool = Field(
            description="是否包含保密条款",
            example=True
        )
        
        # 标注质量控制
        annotation_confidence: float = Field(
            description="标注置信度",
            ge=0.0,
            le=1.0,
            example=0.95
        )
        
        requires_legal_review: bool = Field(
            description="是否需要法务复审",
            example=False
        )
        
        annotation_notes: Optional[str] = Field(
            description="标注备注",
            ui_widget="textarea",
            default="",
            example="合同结构清晰，关键信息完整，建议通过。"
        )
    
    fields = Fields 