#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LangGraph 代理的记忆化功能
"""

import os
from src.elpis.langgraph_agent import LangGraphElpisAgent

def test_memory():
    """测试记忆化功能"""
    print("=== 测试 LangGraph 代理记忆化功能 ===")
    
    # 创建代理实例，使用固定的 session_id
    session_id = "test_session_001"
    agent = LangGraphElpisAgent(session_id=session_id)
    
    print(f"会话ID: {agent.get_session_id()}")
    print(f"记忆文件路径: {agent._memory_file}")
    
    # 第一轮对话
    print("\n--- 第一轮对话 ---")
    agent.ask("你好，我的名字是张三")
    
    # 第二轮对话
    print("\n--- 第二轮对话 ---")
    agent.ask("你还记得我的名字吗？")
    
    print("\n--- 创建新的代理实例（相同session_id）---")
    # 创建新的代理实例，使用相同的 session_id 来测试记忆加载
    agent2 = LangGraphElpisAgent(session_id=session_id)
    
    # 第三轮对话（使用新实例）
    print("\n--- 第三轮对话（新实例）---")
    agent2.ask("我之前告诉过你我的名字，你还记得吗？")
    
    print("\n--- 清理测试 ---")
    agent2.clear_memory()
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_memory()