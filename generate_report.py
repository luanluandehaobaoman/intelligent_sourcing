#!/usr/bin/env python3
"""
智能寻源控制台展示
"""

import sys
import os
sys.path.append('/home/ubuntu/dewu/intelligent_sourcing')

import logging
from intelligent_sourcing_agent import IntelligentSourcingAgent

def run_sourcing(requirements: str):
    """运行智能寻源并在控制台展示结果"""
    
    # 静默模式
    logging.getLogger().setLevel(logging.ERROR)
    
    print("🚀 智能寻源AI Agent")
    print("=" * 50)
    print(f"📝 采购需求: {requirements}")
    print("⚙️  正在执行智能寻源流程...")
    print()
    
    try:
        # 运行智能寻源
        agent = IntelligentSourcingAgent()
        result = agent.run_intelligent_sourcing(requirements)
        
        if result.get("status") == "error":
            print(f"❌ 执行失败: {result.get('error')}")
            return None
        
        print("✅ 工作流执行完成!")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("智能寻源AI Agent")
        print("=" * 50)
        print("用法: python generate_report.py '采购需求描述'")
        print()
        print("示例:")
        print("  python generate_report.py '寻找武汉地区的云仓储物流服务商，注册资本500万以上'")
        print("  python generate_report.py '寻找上海的软件开发服务商，有5年以上经验'")
        return
    
    requirements = sys.argv[1]
    run_sourcing(requirements)

if __name__ == "__main__":
    main()