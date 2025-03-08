import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.chat_service import ChatService
from app.models.user import UserInfo, UserStatus

@pytest.fixture
def chat_service():
    return ChatService()

@pytest.fixture
def mock_user_info():
    return UserInfo(
        userId="test_user_123",
        userNickName="测试用户",
        aiAgentName="小月",
        status=UserStatus.LOGIN,
        lastUpdateTime=datetime.now().isoformat()
    )

@pytest.mark.asyncio
async def test_get_or_create_memobase_user_new_user(chat_service, mock_user_info):
    # Mock MemoBase 客户端的响应
    chat_service.mb.get_user = Mock(return_value=None)
    chat_service.mb.add_user = Mock(return_value="new_user_id_123")
    chat_service.mb.get_user = Mock(return_value={
        "user_id": "new_user_id_123",
        "agent_name": "小月",
        "emotions": []
    })
    chat_service.user_service.update_user = Mock()

    # 测试创建新用户
    result = await chat_service.get_or_create_memobase_user(mock_user_info)
    
    # 验证结果
    assert isinstance(result, dict)
    assert "emotions" in result
    assert chat_service.mb.add_user.called
    assert chat_service.user_service.update_user.called

@pytest.mark.asyncio
async def test_get_or_create_memobase_user_existing_user(chat_service, mock_user_info):
    # 设置现有用户的 agentId
    mock_user_info.agentId = "existing_user_123"
    
    # Mock MemoBase 客户端的响应
    chat_service.mb.get_user = Mock(return_value={
        "user_id": "existing_user_123",
        "agent_name": "小月",
        "emotions": []
    })

    # 测试获取现有用户
    result = await chat_service.get_or_create_memobase_user(mock_user_info)
    
    # 验证结果
    assert isinstance(result, dict)
    assert "emotions" in result
    assert not chat_service.mb.add_user.called

@pytest.mark.asyncio
async def test_get_or_create_memobase_user_error_handling(chat_service, mock_user_info):
    # Mock MemoBase 客户端抛出异常
    chat_service.mb.get_user = Mock(side_effect=Exception("MemoBase connection error"))
    
    # 测试错误处理
    result = await chat_service.get_or_create_memobase_user(mock_user_info)
    
    # 验证结果
    assert isinstance(result, dict)
    assert "emotions" in result
    assert result["emotions"] == []