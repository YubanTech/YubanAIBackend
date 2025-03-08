from typing import List, Dict, Any
import httpx
from datetime import datetime
from app.core.config import settings

class DifyClient:
    def __init__(self):
        self.base_url = settings.DIFY_API_BASE_URL
        self.api_key = settings.DIFY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def send_message(self, message: str, user: str, userNickName: str, agent_name: str = None, conversation_id: str = None) -> Dict[str, Any]:
        """发送消息并获取回复"""
        async with httpx.AsyncClient(timeout=30.0) as client:  # 设置30秒超时
            print(f"正在发送消息...conversation_id为", conversation_id)
            try:
                request_data = {
                    "query": message,
                    "inputs": {
                        "agent_name": agent_name,
                        "userNickName": userNickName,
                    },
                    "user": user,
                    "response_mode": "blocking"
                }
                
                if conversation_id:
                    request_data["conversation_id"] = conversation_id
                
                try:
                    response = await client.post(
                        f"{self.base_url}/chat-messages",
                        headers=self.headers,
                        json=request_data
                    )
                    
                    print(f"发送消息响应状态码: {response.status_code}")
                    print(f"发送消息响应内容: {response.text}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"解析后的响应数据: {data}")
                        return data
                    else:
                        raise ValueError(f"API返回非200状态码: {response.status_code}, 响应内容: {response.text}")
                        
                except httpx.TimeoutException as e:
                    print(f"请求超时: {str(e)}")
                    raise
                except httpx.RequestError as e:
                    print(f"请求错误: {str(e)}")
                    raise
                
            except Exception as e:
                print(f"发送消息时出错，详细错误: {str(e)}")
                print(f"错误类型: {type(e)}")
                raise

    async def get_message_history(self, user: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取用户的消息历史"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/messages",
                    headers=self.headers,
                    params={
                        "user": user,
                        "limit": limit
                    }
                )
                data = response.json()
                return data.get("data", [])
            except Exception as e:
                print(f"获取消息历史时出错: {str(e)}")
                return []