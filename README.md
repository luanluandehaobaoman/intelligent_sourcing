# 智能寻源AI Agent

基于Strands Agents框架的智能采购供应商寻源系统，使用AWS Bedrock Claude模型，通过workflow工具协调多个专门化任务，实现自动化采购供应商发现、评估和筛选。

## 🚀 特性

- **智能需求解析**: 自动解析复杂采购需求文档，提取关键信息
- **博查AI搜索**: 集成博查AI搜索API，多维度精准发现潜在供应商
- **天眼查资质校验**: 通过天眼查API获取企业完整档案和风险评估
- **自动化工作流**: 使用Strands workflow实现任务协调和并行执行
- **标准化报告**: 生成包含15个标准指标的供应商对比分析表格
- **控制台展示**: 直接在控制台展示完整的供应商搜索结果和AI建议

## 📋 系统架构

```
采购需求输入 → 主Agent → workflow工具 → 并行任务执行
                           ↓
                   TaskExecutor (2-8线程)
                   ├── 需求解析Agent (parse_requirements)
                   ├── 供应商搜索Agent (search_suppliers)
                   ├── 资质校验Agent (validate_qualifications)
                   └── 报告生成Agent (generate_report)
                           ↓
                   控制台展示结果 (标准化对比表格)
```

## 🛠️ 环境配置

### 1. 环境要求

- Python 3.10+
- 配置好的AWS账户（用于Bedrock模型访问）
- 博查AI API密钥
- 天眼查API密钥（可选，默认使用Mock数据）

### 2. 安装步骤

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd intelligent_sourcing

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖包
pip install -r requirements.txt
```

### 3. 环境配置

复制环境变量模板并配置：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
```

`.env` 文件配置说明：

```bash
# 博查AI API配置 (必须)
BOCHA_API_KEY=your_bocha_api_key_here  # 从博查AI开放平台获取
BOCHA_BASE_URL=https://api.bochaai.com/v1

# 天眼查API配置 (可选)
TIANYANCHA_USE_MOCK=true  # 设为false使用真实API
TIANYANCHA_API_TOKEN=your_tianyancha_token_here

# AWS Bedrock配置 (必须)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# 系统配置
MAX_SUPPLIERS_TO_ANALYZE=5
REQUEST_TIMEOUT=30
MAX_RETRIES=3
CACHE_TTL_MINUTES=60
LOG_LEVEL=INFO
```

### 4. AWS配置

确保AWS凭据配置正确：

```bash
# 方法1: 使用AWS CLI配置
aws configure --profile default

# 方法2: 设置环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

## 🎯 使用方法

### 基本使用

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行智能寻源
python generate_report.py "您的采购需求描述"
```

### 使用示例

```bash
# 物流仓储类
python generate_report.py "寻找武汉地区的云仓储物流服务商，注册资本500万以上，具备消防资质"

# 软件开发类  
python generate_report.py "寻找北京地区的软件开发服务商，有5年以上经验，团队规模50人以上"

# 制造服务类
python generate_report.py "寻找深圳的电子制造服务商，ISO9001认证，年产能100万件以上"

# 复杂需求示例
python generate_report.py "基本资质要求：成立年限≥3年，注册资本≥200W。需求：武汉自有仓转云仓，丙二类消防资质，恒温存储(22°C±5°C)，距离万纬武汉空港物流园20km内"
```

## 📊 输出结果

运行后会在控制台直接显示：

1. **需求解析结果** - JSON格式的结构化需求分析
2. **供应商搜索过程** - 多维度关键词搜索执行情况
3. **企业资质校验** - 天眼查API验证结果
4. **标准化对比表格** - 包含15个评估指标的供应商对比表
5. **采购建议和风险提示** - AI生成的专业分析建议

### 标准化15个评估指标

| 指标 | 说明 | 数据源 |
|------|------|--------|
| 注册资本 | 企业注册资本金额 | 天眼查API |
| 成立年限 | 从成立至今的年数 | 天眼查API |
| 公司规模 | 员工数量规模 | 天眼查API |
| 销售联系人&联系方式 | 销售对接人信息 | 博查AI搜索 |
| 价格水平 | 价格定位水平 | 标记"未知" |
| 财务风险 | 财务风险等级评估 | 天眼查API |
| 诉讼风险 | 诉讼记录分析 | 天眼查API |
| 年销售额 | 年度销售收入 | 天眼查API |
| 消防资质 | 消防相关资质证书 | 天眼查API |
| 自有运营人数 | 实际运营人员数量 | 综合评估 |
| 自营云仓总面积 | 云仓储面积规模 | 博查AI搜索 |
| 电商客户合作数量 | 电商客户案例数 | 博查AI搜索 |
| 仓内自动化程度 | 自动化技术水平 | 博查AI搜索 |
| 企业口碑 | 市场口碑评价 | 综合评估 |
| 商业模式 | B2B/B2C业务模式 | 综合分析 |


## 🔧 工作流程详解

### 1. 需求解析 (parse_requirements)
- 智能解析复杂采购需求文档
- 提取基本资质要求（成立年限、注册资本等）
- 识别地理位置、业务类型、特殊技术要求
- 生成多维度搜索关键词策略

### 2. 供应商搜索 (search_suppliers)
- 使用博查AI搜索API进行多轮精准搜索
- 多维度关键词组合策略：
  - 地理位置 + 核心业务类型
  - 地理位置 + 特殊技术要求
  - 地理位置 + 资质认证要求
  - 核心业务 + 专业服务能力
- 至少执行5-8次不同维度的搜索
- 去重并筛选最相关的候选供应商

### 3. 资质校验 (validate_qualifications)
- 天眼查API批量查询企业工商信息
- 获取财务风险、诉讼风险评估
- 收集知识产权和资质证书信息
- 风险等级划分和综合评估

### 4. 报告生成 (generate_report)
- 整合所有收集的真实数据
- 生成标准化供应商对比表格
- 提供采购建议和风险提示
- 未获取信息标记为"未知"

## 🔒 安全说明

- ✅ 所有敏感信息通过环境变量管理
- ✅ `.env`文件已加入`.gitignore`
- ✅ 提供`.env.example`模板文件
- ✅ 代码中无硬编码API密钥
- ⚠️ 请确保不要将`.env`文件提交到Git仓库

