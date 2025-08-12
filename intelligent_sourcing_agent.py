#!/usr/bin/env python3
"""
智能寻源AI Agent
基于Strands Agents框架的智能寻源AI Agent，使用AWS Bedrock Claude Sonnet 3.7模型，
通过workflow工具协调多个专门化任务，实现自动化采购供应商发现、评估和筛选。
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv

from strands import Agent, tool
from strands_tools import workflow
from bocha_api import BochaSearchService, extract_companies_from_search_result
from tianyancha import TianyanchaService

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntelligentSourcingAgent:
    """智能寻源AI Agent主类"""
    
    def __init__(self):
        """初始化智能寻源Agent"""
        # 配置模型
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
        
        # 创建API服务实例
        self.bocha_service = BochaSearchService(
            api_key=os.getenv("BOCHA_API_KEY"),
            base_url=os.getenv("BOCHA_BASE_URL", "https://api.bochaai.com/v1")
        )
        
        self.tianyancha_service = TianyanchaService(
            use_mock=os.getenv("TIANYANCHA_USE_MOCK", "true").lower() == "true",
            api_token=os.getenv("TIANYANCHA_API_TOKEN")
        )
        
        # 创建自定义工具（必须在创建Agent之前）
        self._create_tools()
        
        # 创建主Agent，包含所有工具
        self.main_agent = Agent(
            model=self.model_id,
            tools=[workflow, self.bocha_supplier_search_tool, self.tianyancha_company_validate_tool],
            system_prompt="""你是智能寻源专家，负责协调多个任务完成供应商发现和评估。
            
            你拥有以下工具：
            1. workflow - 工作流协调工具
            2. bocha_supplier_search - 博查AI供应商搜索工具
            3. tianyancha_company_validate - 天眼查企业校验工具
            
            请严格按照工作流程执行，确保调用正确的工具获取真实数据。"""
        )
        
        logger.info("智能寻源AI Agent初始化完成")
    
    def _create_tools(self):
        """创建自定义工具"""
        
        # 创建博查AI搜索工具
        @tool
        def bocha_supplier_search(query: str, count: int = 10) -> str:
            """
            使用博查AI搜索供应商信息
            Args:
                query: 动态生成的搜索查询词
                count: 返回结果数量(最多50)
            Returns:
                结构化的供应商信息JSON
            """
            try:
                logger.info(f"🔍 开始博查AI搜索: {query}")
                
                # 执行AI搜索
                search_result = self.bocha_service.ai_search(
                    query=query,
                    count=min(count, 50),
                    freshness="month",  # 搜索近一个月的信息
                    answer=False  # 不需要生成AI答案，只要搜索结果
                )
                
                # 提取企业信息
                companies = extract_companies_from_search_result(search_result)
                
                logger.info(f"✅ 博查AI搜索完成，找到 {len(companies)} 家企业")
                
                return json.dumps({
                    "status": "success",
                    "supplier_count": len(companies),
                    "suppliers": companies
                }, ensure_ascii=False)
                
            except Exception as e:
                error_msg = f"博查AI搜索失败: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return json.dumps({
                    "status": "error", 
                    "error": error_msg,
                    "suppliers": []
                }, ensure_ascii=False)
        
        # 创建天眼查校验工具
        @tool  
        def tianyancha_company_validate(company_name: str) -> str:
            """
            通过天眼查API获取企业全面信息
            Args:
                company_name: 企业名称
            Returns:
                包含基本信息、风险评估、财务数据的完整企业档案JSON
            """
            try:
                logger.info(f"🏢 开始天眼查校验: {company_name}")
                
                # 获取企业基本信息
                basic_info = self.tianyancha_service.get_company_basic_info(company_name)
                
                # 获取风险信息
                risk_info = self.tianyancha_service.get_company_risk_info(company_name)
                
                # 获取知识产权信息
                ip_info = self.tianyancha_service.get_intellectual_property(company_name)
                
                # 获取财务数据
                financial_info = self.tianyancha_service.get_financial_data(company_name)
                
                # 整合所有信息
                company_profile = {
                    "company_name": company_name,
                    "basic_info": basic_info.get("result", {}),
                    "risk_info": risk_info.get("result", {}),
                    "intellectual_property": ip_info.get("result", {}),
                    "financial_data": financial_info.get("result", {}),
                    "validation_status": "completed" if basic_info.get("error_code") == 0 else "failed"
                }
                
                logger.info(f"✅ 天眼查校验完成: {company_name}")
                
                return json.dumps(company_profile, ensure_ascii=False)
                
            except Exception as e:
                error_msg = f"天眼查校验失败: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return json.dumps({
                    "company_name": company_name,
                    "validation_status": "error",
                    "error": error_msg,
                    "basic_info": {},
                    "risk_info": {}
                }, ensure_ascii=False)
        
        # 保存工具引用，供后续使用
        self.bocha_supplier_search_tool = bocha_supplier_search
        self.tianyancha_company_validate_tool = tianyancha_company_validate
        
        # 为了兼容性，也保留原名称
        self.bocha_supplier_search = bocha_supplier_search
        self.tianyancha_company_validate = tianyancha_company_validate
    
    def create_sourcing_workflow(self, procurement_requirements: str) -> str:
        """
        创建智能寻源工作流
        Args:
            procurement_requirements: 采购需求描述
        Returns:
            工作流ID
        """
        logger.info("创建智能寻源工作流")
        
        # 定义工作流任务
        workflow_tasks = [
            {
                "task_id": "parse_requirements",
                "description": f"""解析以下采购需求文档，提取关键信息并生成搜索策略：
                
采购需求：
{procurement_requirements}

请提取以下关键信息：
1. 基本资质要求（成立年限、注册资本等）
2. 地理位置要求
3. 业务类型和行业要求
4. 特殊技术或服务要求
5. 生成3-5个有效的搜索关键词组合

输出格式为结构化JSON，包含提取的信息和搜索策略。""",
                "model_provider": "bedrock",
                "model_settings": {"model_id": self.model_id},
                "priority": 5,
                "timeout": 180
            },
            {
                "task_id": "search_suppliers", 
                "description": f"""【重要】你必须使用bocha_supplier_search工具进行供应商搜索！根据复杂需求制定精准搜索策略！

原始采购需求：{procurement_requirements}

执行步骤：
1. 仔细查看上一步parse_requirements任务的输出结果
2. 从中提取搜索关键词组合，如果没有则根据原始需求分析生成多个精准关键词
3. 针对复杂需求，必须使用多维度关键词搜索策略：
   - 地理位置 + 核心业务类型组合
   - 地理位置 + 特殊技术要求组合  
   - 地理位置 + 资质认证要求组合
   - 地理位置 + 行业细分领域组合
   - 核心业务 + 专业服务能力组合
4. 根据需求复杂度，对每个关键词调用bocha_supplier_search工具，参数格式：bocha_supplier_search(query="具体关键词", count=15)
5. 至少执行5-8次不同维度的关键词搜索，确保覆盖需求的各个重要方面
6. 整合所有搜索结果，去重并筛选出最相关的候选供应商

【搜索策略】：
- 从需求解析结果中提取地理位置、业务类型、特殊要求、资质要求等关键信息
- 将这些信息组合成不同的搜索关键词，确保搜索的全面性和精准性
- 不要使用过于简单的关键词，要体现需求的专业性和特殊性

【必须使用工具】：请确保调用bocha_supplier_search工具获取真实数据，不要生成虚假信息！

输出格式：供应商基本信息的结构化列表，包含公司名称、来源URL、描述等。""",
                "dependencies": ["parse_requirements"],
                "tools": ["bocha_supplier_search"],
                "model_provider": "bedrock",
                "model_settings": {"model_id": self.model_id},
                "priority": 4,
                "timeout": 300
            },
            {
                "task_id": "validate_qualifications",
                "description": f"""【重要】你必须使用tianyancha_company_validate工具进行企业校验！

原始采购需求：{procurement_requirements}

执行步骤：
1. 仔细查看上一步search_suppliers的输出结果
2. 提取出找到的供应商公司名称列表
3. 对每家供应商调用tianyancha_company_validate工具，参数格式：tianyancha_company_validate(company_name="公司名称")
4. 收集所有企业的基本工商信息、财务风险、诉讼风险、知识产权等数据
5. 根据采购需求对每家供应商进行综合评估和风险等级划分

【必须使用工具】：请确保调用tianyancha_company_validate工具获取真实企业数据，不要生成虚假信息！

输出格式：每家供应商的详细资质档案，包含基本信息、风险级别、财务状况等。""",
                "dependencies": ["search_suppliers"],
                "tools": ["tianyancha_company_validate"],
                "model_provider": "bedrock",
                "model_settings": {"model_id": self.model_id},
                "priority": 4,
                "timeout": 300
            },
            {
                "task_id": "generate_report",
                "description": f"""整合前面所有真实数据，生成标准化供应商对比表格。

原始采购需求：{procurement_requirements}

执行步骤：
1. 查看parse_requirements的需求解析结果
2. 查看search_suppliers的供应商搜索结果
3. 查看validate_qualifications的企业校验结果
4. 基于这些真实数据生成对比表格

按照以下标准化schema生成供应商对比表格：

```python
output_schema = {{
    "表格标题": "武汉云仓储物流服务商对比表",
    "列标题": ["指标", "供应商A", "供应商B", "供应商C", "供应商D"],
    "行指标": [
        "注册资本",           # 天眼查API - 基本工商信息
        "成立年限",           # 天眼查API - 计算得出
        "公司规模",           # 天眼查API - 员工数量
        "销售联系人&联系方式", # 博查AI搜索 - 联系信息
        "价格水平",           # 标记"未知" - 需单独询价
        "财务风险",           # 天眼查API - 风险评估等级
        "诉讼风险",           # 天眼查API - 诉讼记录分析
        "年销售额",           # 天眼查API - 年报数据
        "消防资质",           # 天眼查API - 资质证书
        "自有运营人数",        # 博查AI/天眼查 - 运营规模
        "自营云仓总面积",      # 博查AI搜索 - 业务信息
        "电商客户合作数量",    # 博查AI搜索 - 客户案例
        "仓内自动化程度",      # 博查AI搜索 - 技术水平
        "企业口碑",           # 综合评估 - 基于多方信息
        "商业模式"            # 博查AI搜索 - B2C/B2B业务
    ]
}}
```

数据处理规则：
- **确定数据**: API直接获取的准确信息
- **计算数据**: 基于现有信息推算 (如成立年限)
- **未知数据**: 无法获取时明确标记"未知"，绝不编造
- **风险评估**: 基于天眼查数据进行等级划分 (低/中/高)

【重要要求】：
- 严格按照上述schema生成标准化表格
- 只使用前面任务获取的真实数据
- 未获取到的信息必须标记为"未知"
- 不要编造或假设任何数据
- 提供采购建议和风险提示

输出标准化的Markdown表格格式。""",
                "dependencies": ["validate_qualifications"],
                "model_provider": "bedrock",
                "model_settings": {"model_id": self.model_id},
                "system_prompt": "你是专业的采购报告生成专家，严格按照表格格式输出，只使用真实数据，未知信息标记为'未知'",
                "priority": 5,
                "timeout": 240
            }
        ]
        
        # 先尝试删除可能存在的旧工作流
        try:
            self.main_agent.tool.workflow(
                action="delete",
                workflow_id="intelligent_sourcing_pipeline"
            )
        except:
            pass
        
        # 创建工作流
        result = self.main_agent.tool.workflow(
            action="create", 
            workflow_id="intelligent_sourcing_pipeline",
            tasks=workflow_tasks
        )
        
        if result.get("status") == "success":
            logger.info("智能寻源工作流创建成功")
            return "intelligent_sourcing_pipeline"
        else:
            error_msg = f"工作流创建失败: {result.get('content', [{}])[0].get('text', '未知错误')}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def execute_sourcing_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        执行智能寻源工作流
        Args:
            workflow_id: 工作流ID
        Returns:
            执行结果
        """
        logger.info(f"开始执行智能寻源工作流: {workflow_id}")
        
        # 启动工作流
        result = self.main_agent.tool.workflow(
            action="start", 
            workflow_id=workflow_id
        )
        
        if result.get("status") == "success":
            logger.info("智能寻源工作流执行完成")
            return result
        else:
            error_msg = f"工作流执行失败: {result.get('content', [{}])[0].get('text', '未知错误')}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        获取工作流状态
        Args:
            workflow_id: 工作流ID
        Returns:
            工作流状态信息
        """
        return self.main_agent.tool.workflow(
            action="status",
            workflow_id=workflow_id
        )
    
    def run_intelligent_sourcing(self, procurement_requirements: str) -> Dict[str, Any]:
        """
        运行完整的智能寻源流程
        Args:
            procurement_requirements: 采购需求描述
        Returns:
            寻源结果
        """
        try:
            logger.info("=== 开始智能寻源流程 ===")
            
            # 创建工作流
            workflow_id = self.create_sourcing_workflow(procurement_requirements)
            
            # 执行工作流
            result = self.execute_sourcing_workflow(workflow_id)
            
            # 获取最终状态
            final_status = self.get_workflow_status(workflow_id)
            
            logger.info("=== 智能寻源流程完成 ===")
            
            return {
                "workflow_id": workflow_id,
                "execution_result": result,
                "final_status": final_status
            }
            
        except Exception as e:
            error_msg = f"智能寻源流程执行失败: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }


def main():
    """主函数 - 命令行交互"""
    print("🤖 智能寻源AI Agent")
    print("=" * 50)
    print("基于Strands Agents框架，集成博查AI搜索和天眼查API")
    print("支持自动化采购供应商发现、评估和筛选")
    print()
    
    try:
        # 初始化Agent
        print("⚙️  正在初始化智能寻源Agent...")
        agent = IntelligentSourcingAgent()
        print("✅ Agent初始化完成")
        print()
        
        while True:
            print("📝 请输入采购需求描述（输入 'quit' 退出）:")
            print("例如：寻找华南地区的云仓储物流服务商，要求注册资本不少于500万，成立时间3年以上")
            print()
            
            user_input = input(">>> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
            
            if not user_input:
                print("❌ 请输入有效的采购需求描述")
                continue
            
            print()
            print("🚀 开始执行智能寻源...")
            print("-" * 50)
            
            # 执行智能寻源
            result = agent.run_intelligent_sourcing(user_input)
            
            if result.get("status") == "error":
                print(f"❌ 执行失败: {result.get('error')}")
            else:
                print("✅ 智能寻源完成!")
                print()
                print("📊 执行结果:")
                
                # 显示工作流状态
                final_status = result.get("final_status", {})
                if final_status.get("status") == "success":
                    status_content = final_status.get("content", [{}])[0].get("text", "")
                    print(status_content)
                else:
                    print("状态信息获取失败")
            
            print()
            print("=" * 50)
            print()
    
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序执行错误: {str(e)}")
        logger.error(f"程序执行错误: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()