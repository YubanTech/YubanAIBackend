import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memobase import MemoBaseClient
from datetime import datetime
from app.core.config import settings

def test_memobase_create_user():
    # 初始化 MemoBase 客户端
    print("初始化 MemoBase 客户端...")
    mb = MemoBaseClient(
        project_url=settings.MEMOBASE_PROJECT_URL,
        api_key=settings.MEMOBASE_PROJECT_TOKEN
    )
    
    # 测试连接
    print("\n测试 MemoBase 连接...")
    try:
        assert mb.ping()
        print("MemoBase 连接成功")
    except Exception as e:
        print(f"MemoBase 连接失败: {str(e)}")
        return
    
    # 创建测试用户数据
    test_user_data = {
        "user_id": f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "agent_name": "小月",
        "created_at": datetime.now().isoformat(),
        "emotions": []
    }
    
    print(f"\n准备创建用户，数据：{test_user_data}")
    
    try:
        # 创建用户
        uid = mb.add_user(test_user_data)
        print(f"创建用户成功，返回的 uid: {uid}")
        print(f"uid 类型: {type(uid)}")
        
        # 获取创建的用户
        user = mb.get_user(uid)
        print(f"\n获取创建的用户信息:")
        print(f"用户数据: {user}")
        print(f"用户数据类型: {type(user)}")
        
    except Exception as e:
        print(f"\n创建用户过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_memobase_create_user()