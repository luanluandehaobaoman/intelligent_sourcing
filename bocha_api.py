"""
博查AI搜索API集成服务
基于博查AI开放平台的搜索API实现供应商智能搜索功能
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BochaSearchService:
    """博查AI搜索服务"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.bochaai.com/v1"):
        """
        初始化博查搜索服务
        
        Args:
            api_key: 从博查AI开放平台获取的API-KEY
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        logger.info(f"初始化博查AI搜索服务: {base_url}")
    
    def ai_search(self, query: str, freshness: str = "noLimit", 
                  count: int = 10, answer: bool = False, 
                  stream: bool = False) -> Dict[str, Any]:
        """
        AI Search - 进行高级搜索（AI搜）
        
        Args:
            query: 搜索关键词
            freshness: 搜索时间范围 ("noLimit", "day", "week", "month", "year")
            count: 返回结果数量，最多50
            answer: 是否生成AI答案
            stream: 是否使用流式输出
            
        Returns:
            搜索结果，包含网页、图片、模态卡等
        """
        endpoint = f"{self.base_url}/ai-search"
        payload = {
            "query": query,
            "freshness": freshness,
            "count": min(count, 50),
            "answer": answer,
            "stream": stream
        }
        
        logger.info(f"执行AI搜索: {query}, count={count}, freshness={freshness}")
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            result = self._handle_response(response)
            
            logger.info(f"搜索完成: 状态码={response.status_code}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("博查AI搜索请求超时")
            raise Exception("博查AI搜索请求超时")
        except requests.exceptions.RequestException as e:
            logger.error(f"博查AI搜索请求失败: {e}")
            raise Exception(f"博查AI搜索请求失败: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理API响应"""
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.error("响应JSON解析失败")
                raise Exception("博查AI响应格式错误")
        else:
            error_msg = f"API调用失败: {response.status_code}"
            try:
                error_detail = response.json()
                if 'error' in error_detail:
                    error_msg += f" - {error_detail['error']}"
            except:
                error_msg += f" - {response.text[:200]}"
            
            logger.error(error_msg)
            raise Exception(error_msg)


def extract_companies_from_search_result(search_response: Dict[str, Any]) -> list:
    """
    从博查AI搜索结果中提取企业信息
    
    Args:
        search_response: 博查AI的搜索响应
        
    Returns:
        提取到的企业信息列表
    """
    companies = []
    
    try:
        if not search_response.get('messages'):
            logger.warning("搜索响应中没有messages字段")
            return companies
            
        for message in search_response['messages']:
            if message.get('type') == 'source' and message.get('content_type') == 'webpage':
                try:
                    content = json.loads(message['content'])
                    if 'value' in content:
                        for item in content['value']:
                            company_info = _extract_company_from_item(item)
                            if company_info:
                                companies.append(company_info)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"解析搜索结果项失败: {e}")
                    continue
    
    except Exception as e:
        logger.error(f"提取企业信息失败: {e}")
    
    # 去重处理
    companies = _remove_duplicate_companies(companies)
    
    logger.info(f"从搜索结果中提取到 {len(companies)} 家企业")
    return companies


def _extract_company_from_item(item: Dict) -> Optional[Dict]:
    """从单个搜索结果项中提取企业信息"""
    try:
        name = item.get('name', '')
        snippet = item.get('snippet', '')
        url = item.get('url', '')
        
        # 简单的企业名称检测
        if any(suffix in name for suffix in ['有限公司', '股份有限公司', '有限责任公司', '集团']):
            return {
                "company_name": name,
                "source_url": url,
                "description": snippet,
                "source": "bocha_search",
                "confidence": 0.8
            }
        
        return None
    except Exception as e:
        logger.warning(f"提取企业信息失败: {e}")
        return None


def _remove_duplicate_companies(companies: list) -> list:
    """去重处理，基于公司名称"""
    seen_names = set()
    unique_companies = []
    
    for company in companies:
        name = company.get('company_name', '')
        # 提取核心公司名称（去掉标题中的多余信息）
        core_name = name.split('】')[0].split('【')[-1] if '】' in name else name
        
        if core_name not in seen_names:
            seen_names.add(core_name)
            # 更新为清理后的名称
            company['company_name'] = core_name
            unique_companies.append(company)
    
    return unique_companies