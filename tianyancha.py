"""
天眼查API Mock服务
模拟天眼查API响应，提供企业基本信息、财务数据、风险信息等
"""

import random
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class TianyanchaMockAPI:
    def __init__(self):
        self.mock_data = {
            "companies": self._generate_mock_companies(),
            "risk_data": self._generate_risk_data(),
            "financial_data": self._generate_financial_data(),
            "intellectual_property": self._generate_ip_data()
        }
    
    def get_company_basic_info(self, company_name: str) -> Dict[str, Any]:
        """
        获取企业基本信息
        接口ID：1116
        价格：¥ 0.15/次
        
        Args:
            company_name: 企业名称
            
        Returns:
            企业基本信息
        """
        # 模拟API响应延迟
        import time
        time.sleep(0.1)
        
        # 查找匹配的企业
        company_data = self._find_company_by_name(company_name)
        
        if not company_data:
            return {
                "error_code": 300204,
                "reason": "查无结果",
                "result": None
            }
        
        return {
            "error_code": 0,
            "reason": "success",
            "result": {
                "name": company_data["name"],
                "type": company_data["type"],
                "regStatus": company_data["regStatus"],
                "establishTime": company_data["establishTime"],
                "regCapital": company_data["regCapital"],
                "actualCapital": company_data["actualCapital"],
                "legalPersonName": company_data["legalPersonName"],
                "regNumber": company_data["regNumber"],
                "creditCode": company_data["creditCode"],
                "orgNumber": company_data["orgNumber"],
                "taxNumber": company_data["taxNumber"],
                "businessScope": company_data["businessScope"],
                "regLocation": company_data["regLocation"],
                "industry": company_data["industry"],
                "approvedTime": company_data["approvedTime"],
                "fromTime": company_data["fromTime"],
                "toTime": company_data["toTime"],
                "staffNumRange": company_data["staffNumRange"],
                "companyId": company_data["companyId"]
            }
        }
    
    def get_company_risk_info(self, company_name: str) -> Dict[str, Any]:
        """
        获取企业天眼风险信息
        接口ID：1058
        价格：¥ 6/次
        
        Args:
            company_name: 企业名称
            
        Returns:
            风险信息列表
        """
        import time
        time.sleep(0.15)
        
        company_id = self._get_company_id(company_name)
        if not company_id:
            return {
                "error_code": 300204,
                "reason": "查无结果",
                "result": None
            }
        
        risk_data = self.mock_data["risk_data"].get(company_id, [])
        
        return {
            "error_code": 0,
            "reason": "success",
            "result": {
                "total": len(risk_data),
                "riskList": risk_data
            }
        }
    
    def get_intellectual_property(self, company_name: str) -> Dict[str, Any]:
        """
        获取企业知识产权信息
        接口ID：1139
        价格：¥ 1.5/次
        
        Args:
            company_name: 企业名称
            
        Returns:
            知识产权信息，包含商标、专利、著作权等
        """
        import time
        time.sleep(0.12)
        
        company_id = self._get_company_id(company_name)
        if not company_id:
            return {
                "error_code": 300204,
                "reason": "查无结果",
                "result": None
            }
        
        ip_data = self.mock_data["intellectual_property"].get(company_id, {})
        
        return {
            "error_code": 0,
            "reason": "success",
            "result": {
                "trademark": ip_data.get("trademark", []),
                "patent": ip_data.get("patent", []),
                "copyright": ip_data.get("copyright", []),
                "softwareCopyright": ip_data.get("softwareCopyright", []),
                "website": ip_data.get("website", [])
            }
        }
    
    def get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """
        获取企业财务数据（模拟接口，实际天眼查可能需要更高权限）
        
        Args:
            company_name: 企业名称
            
        Returns:
            财务数据
        """
        import time
        time.sleep(0.2)
        
        company_id = self._get_company_id(company_name)
        if not company_id:
            return {
                "error_code": 300204,
                "reason": "查无结果",
                "result": None
            }
        
        financial_data = self.mock_data["financial_data"].get(company_id, {})
        
        return {
            "error_code": 0,
            "reason": "success",
            "result": financial_data
        }
    
    def _find_company_by_name(self, company_name: str) -> Optional[Dict]:
        """根据企业名称查找企业数据"""
        for company in self.mock_data["companies"]:
            if company["name"] == company_name or company_name in company["name"]:
                return company
        return None
    
    def _get_company_id(self, company_name: str) -> Optional[str]:
        """获取企业ID"""
        company = self._find_company_by_name(company_name)
        return company["companyId"] if company else None
    
    def _generate_mock_companies(self) -> List[Dict]:
        """生成模拟企业数据"""
        import random
        
        # 基础模板数据
        templates = [
            {
                "name_template": "{city}{type}物流有限公司",
                "business_scope": "仓储服务（不含危险化学品）;货物配送;供应链管理服务;物流信息咨询服务",
                "industry": "交通运输、仓储和邮政业"
            },
            {
                "name_template": "{province}{brand}仓储服务有限公司", 
                "business_scope": "仓储服务;货物运输;快递服务;供应链管理;冷链物流服务",
                "industry": "交通运输、仓储和邮政业"
            },
            {
                "name_template": "{city}智慧物流园管理有限公司",
                "business_scope": "物流园区管理;仓储服务;货物配送;物流信息平台运营;智能仓储系统开发", 
                "industry": "交通运输、仓储和邮政业"
            },
            {
                "name_template": "{province}现代物流集团有限公司",
                "business_scope": "现代物流服务;仓储管理;运输代理;供应链金融服务;物流装备租赁",
                "industry": "交通运输、仓储和邮政业"
            },
            {
                "name_template": "{city}云仓科技有限公司",
                "business_scope": "云仓储服务;智能物流技术开发;仓储管理软件开发;电商仓储服务;代发货服务",
                "industry": "软件和信息技术服务业"
            }
        ]
        
        # 动态城市和品牌名称
        cities = ["深圳", "上海", "北京", "广州", "杭州", "成都", "重庆", "西安", "南京", "武汉"]
        provinces = ["广东省", "浙江省", "江苏省", "山东省", "河南省", "湖北省", "四川省", "福建省"]
        types = ["中部云仓", "速达云仓", "智通云仓", "安捷云仓", "现代云仓"]
        brands = ["顺丰", "中通", "申通", "圆通", "韵达", "德邦", "京东", "菜鸟"]
        legal_persons = ["张建华", "李明强", "王海涛", "陈国强", "刘晓敏", "赵志强", "孙美丽", "周天宇"]
        
        companies = []
        for i, template in enumerate(templates, 1):
            city = random.choice(cities)
            province = random.choice(provinces)
            
            # 生成公司名称
            if "{city}" in template["name_template"]:
                company_name = template["name_template"].format(
                    city=city, 
                    type=random.choice(types),
                    brand=random.choice(brands)
                )
            else:
                company_name = template["name_template"].format(
                    province=province,
                    brand=random.choice(brands)
                )
            
            # 生成随机注册资本
            capitals = [100, 200, 500, 800, 1000, 2000, 5000]
            reg_capital = random.choice(capitals)
            actual_capital = int(reg_capital * random.uniform(0.8, 1.0))
            
            # 生成随机成立时间
            years = list(range(2012, 2025))
            est_year = random.choice(years)
            est_month = random.randint(1, 12)
            est_day = random.randint(1, 28)
            establish_time = f"{est_year}-{est_month:02d}-{est_day:02d}"
            
            # 生成员工规模
            staff_ranges = ["1-9人", "10-49人", "50-99人", "100-499人", "500-999人", "1000-4999人"]
            
            company = {
                "name": company_name,
                "type": "有限责任公司",
                "regStatus": "存续",
                "establishTime": establish_time,
                "regCapital": f"{reg_capital}万人民币",
                "actualCapital": f"{actual_capital}万人民币", 
                "legalPersonName": random.choice(legal_persons),
                "regNumber": f"420{random.randint(100, 999)}{random.randint(100000, 999999)}",
                "creditCode": f"914201{random.randint(10, 99)}MA4{chr(65+i)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(10, 99)}",
                "orgNumber": f"MA4{chr(65+i)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-{i}",
                "taxNumber": f"914201{random.randint(10, 99)}MA4{chr(65+i)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(10, 99)}",
                "businessScope": template["business_scope"], 
                "regLocation": f"{city}市{random.choice(['高新区', '经开区', '新区'])}",
                "industry": template["industry"],
                "approvedTime": establish_time,
                "fromTime": establish_time,
                "toTime": f"{est_year + 30}-{est_month:02d}-{est_day-1:02d}",
                "staffNumRange": random.choice(staff_ranges),
                "companyId": f"company_{str(i).zfill(3)}"
            }
            companies.append(company)
            
        return companies
    
    def _generate_risk_data(self) -> Dict[str, List[Dict]]:
        """生成风险数据"""
        risk_types = [
            "经营异常", "行政处罚", "股权出质", "动产抵押", "欠税公告", 
            "司法拍卖", "失信信息", "限制高消费", "终本案件", "被执行人"
        ]
        
        risk_data = {}
        for i in range(1, 6):
            company_id = f"company_{str(i).zfill(3)}"
            risks = []
            
            # 随机生成0-3个风险项
            num_risks = random.randint(0, 3)
            for _ in range(num_risks):
                risk = {
                    "riskType": random.choice(risk_types),
                    "riskLevel": random.choice(["低", "中", "高"]),
                    "riskContent": f"模拟风险内容 - {random.choice(['合同纠纷', '欠款纠纷', '劳动争议', '行政违规'])}",
                    "publishTime": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                    "riskAmount": f"{random.randint(1, 100)}万元" if random.choice([True, False]) else None
                }
                risks.append(risk)
            
            risk_data[company_id] = risks
        
        return risk_data
    
    def _generate_financial_data(self) -> Dict[str, Dict]:
        """生成财务数据"""
        financial_data = {}
        
        for i in range(1, 6):
            company_id = f"company_{str(i).zfill(3)}"
            
            # 生成近3年财务数据
            years = ["2023", "2022", "2021"]
            financial_data[company_id] = {
                "yearReports": []
            }
            
            for year in years:
                base_revenue = random.randint(1000, 10000)  # 万元
                growth_rate = random.uniform(-0.2, 0.3)
                
                report = {
                    "reportYear": year,
                    "totalRevenue": f"{base_revenue}万元",
                    "netProfit": f"{int(base_revenue * random.uniform(0.05, 0.2))}万元",
                    "totalAssets": f"{int(base_revenue * random.uniform(1.5, 3.0))}万元",
                    "totalLiabilities": f"{int(base_revenue * random.uniform(0.8, 1.8))}万元",
                    "ownerEquity": f"{int(base_revenue * random.uniform(0.7, 1.2))}万元",
                    "cashFlow": f"{int(base_revenue * random.uniform(0.1, 0.4))}万元",
                    "growthRate": f"{growth_rate * 100:.1f}%",
                    "debtRatio": f"{random.uniform(0.3, 0.7) * 100:.1f}%",
                    "roe": f"{random.uniform(0.05, 0.25) * 100:.1f}%"
                }
                financial_data[company_id]["yearReports"].append(report)
        
        return financial_data
    
    def _generate_ip_data(self) -> Dict[str, Dict]:
        """生成知识产权数据"""
        ip_data = {}
        
        trademark_classes = ["35类-广告销售", "39类-运输贮藏", "42类-科技服务"]
        patent_types = ["发明专利", "实用新型专利", "外观设计专利"]
        
        for i in range(1, 6):
            company_id = f"company_{str(i).zfill(3)}"
            
            # 商标信息
            trademarks = []
            for j in range(random.randint(0, 5)):
                trademark = {
                    "trademarkName": f"商标{j+1}",
                    "trademarkNumber": f"TM{random.randint(10000000, 99999999)}",
                    "classNumber": random.choice(trademark_classes),
                    "status": random.choice(["已注册", "申请中", "已驳回"]),
                    "applyDate": (datetime.now() - timedelta(days=random.randint(365, 1095))).strftime("%Y-%m-%d"),
                    "validDate": (datetime.now() + timedelta(days=random.randint(365, 3650))).strftime("%Y-%m-%d")
                }
                trademarks.append(trademark)
            
            # 专利信息
            patents = []
            for j in range(random.randint(0, 8)):
                patent = {
                    "patentName": f"一种{random.choice(['智能', '自动化', '高效'])}{random.choice(['仓储', '物流', '配送'])}方法",
                    "patentNumber": f"CN{random.randint(100000000, 999999999)}",
                    "patentType": random.choice(patent_types),
                    "status": random.choice(["已授权", "实审中", "已公开"]),
                    "applyDate": (datetime.now() - timedelta(days=random.randint(365, 1460))).strftime("%Y-%m-%d"),
                    "authorizeDate": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
                }
                patents.append(patent)
            
            # 软件著作权
            software_copyrights = []
            for j in range(random.randint(0, 3)):
                copyright = {
                    "softwareName": f"{random.choice(['仓储', '物流', '配送'])}管理系统V{j+1}.0",
                    "registrationNumber": f"2023SR{random.randint(100000, 999999)}",
                    "developCompletionDate": (datetime.now() - timedelta(days=random.randint(90, 730))).strftime("%Y-%m-%d"),
                    "registrationDate": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
                }
                software_copyrights.append(copyright)
            
            ip_data[company_id] = {
                "trademark": trademarks,
                "patent": patents,
                "copyright": [],  # 作品著作权通常较少
                "softwareCopyright": software_copyrights,
                "website": []  # 网站备案信息
            }
        
        return ip_data


class TianyanchaService:
    """天眼查服务封装类，提供统一的接口"""
    
    def __init__(self, use_mock: bool = True, api_token: str = None):
        """
        初始化天眼查服务
        
        Args:
            use_mock: 是否使用Mock数据
            api_token: 天眼查API Token（实际使用时需要）
        """
        self.use_mock = use_mock
        self.api_token = api_token
        
        if use_mock:
            self.mock_api = TianyanchaMockAPI()
        else:
            # 实际API实现（需要真实API Key）
            self.base_url = "https://open.tianyancha.com/services/open"
    
    def get_company_basic_info(self, company_name: str) -> Dict[str, Any]:
        """获取企业基本信息"""
        if self.use_mock:
            return self.mock_api.get_company_basic_info(company_name)
        else:
            # 实际API调用实现
            return self._call_real_api("ic/baseinfo/normal", {"keyword": company_name})
    
    def get_company_risk_info(self, company_name: str) -> Dict[str, Any]:
        """获取企业风险信息"""
        if self.use_mock:
            return self.mock_api.get_company_risk_info(company_name)
        else:
            return self._call_real_api("ic/risklist", {"keyword": company_name})
    
    def get_intellectual_property(self, company_name: str) -> Dict[str, Any]:
        """获取知识产权信息"""
        if self.use_mock:
            return self.mock_api.get_intellectual_property(company_name)
        else:
            return self._call_real_api("ic/ipr", {"keyword": company_name})
    
    def get_financial_data(self, company_name: str) -> Dict[str, Any]:
        """获取财务数据"""
        if self.use_mock:
            return self.mock_api.get_financial_data(company_name)
        else:
            # 财务数据可能需要特殊权限
            return {"error": "财务数据需要高级API权限"}
    
    def _call_real_api(self, endpoint: str, params: Dict) -> Dict[str, Any]:
        """调用真实天眼查API"""
        if not self.api_token:
            raise ValueError("使用真实API需要提供api_token")
        
        import requests
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=params, headers=headers)
            return response.json()
        except Exception as e:
            return {
                "error_code": -1,
                "reason": f"API调用失败: {str(e)}",
                "result": None
            }