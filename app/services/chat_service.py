from datetime import datetime
from typing import List, Tuple, Optional
import time
from app.core.config import settings
from app.models.user import UserInfo, UpdateUserRequest
from app.services.user_service import UserService
from app.services.dify_client import DifyClient
from app.db.chat_repository import ChatRepository
from app.models.chat import ChatMessage, ChatHistoryItem
from app.database.mongodb import MongoDB  # Add this import

class ChatService:
    def __init__(self):
        self.use_dify = True
        self.dify_client = DifyClient() if self.use_dify else None
        self.user_service = UserService()
        self.chat_repository = ChatRepository()  # 添加 chat repository
        
        # Initialize OpenAI client as backup
        import openai
        self.client = openai.Client(
            api_key=settings.LINGYIWANWU_API_KEY,
            base_url=settings.LINGYIWANWU_API_BASE
        )

    async def get_agent_name(self, user_id: str) -> str:
        user_info = await self.user_service.get_user(user_id)
        return user_info.aiAgentName if user_info else "小月"

    async def update_agent_name(self, user_id: str, agent_name: str):
        user_info = await self.user_service.get_user(user_id)
        if user_info:
            update_request = UpdateUserRequest(
                userNickName=user_info.userNickName,
                aiAgentName=agent_name,
                agentId=user_info.agentId
            )
            await self.user_service.update_user(user_id, update_request)

    async def get_emotion_history(self, user_id: str) -> str:
        if self.use_dify:
            try:
                messages = await self.dify_client.get_message_history(user=user_id, limit=5)
                if not messages:
                    return "暂无历史情感记录"
                return "\n".join([msg.get("content", "") for msg in messages])
            except Exception as e:
                print(f"获取情感历史失败: {str(e)}")
                return "暂无历史情感记录"

    async def generate_response(self, user_id: str, message: str) -> str:
        print(f"开始处理用户消息，user_id: {user_id}, message: {message}")
        user_info = await self.user_service.get_user(user_id)
        print(f"获取到用户信息: {user_info}")
        if not user_info:
            print("未找到用户信息")
            raise ValueError("User not found")

        try:
            print("开始保存用户消息")
            current_time = datetime.now().isoformat()
            user_message = ChatMessage(
                user_id=user_id,
                role="user",
                content=message,
                agent_name=user_info.aiAgentName,
                created_at=current_time  # 使用 created_at
            )
            await self.chat_repository.save_message(user_message)
            print("用户消息保存成功")

            if self.use_dify:
                print(f"使用 Dify API, conversation_id: {user_info.agentId}")
                conversation_id = user_info.agentId
                print("开始调用 Dify send_message")
                response = await self.dify_client.send_message(
                    message=message,
                    user=user_id,
                    userNickName=user_info.userNickName,
                    agent_name=user_info.aiAgentName,
                    conversation_id=conversation_id
                )
                print(f"Dify 响应: {response}")
                
                if not conversation_id and response.get("conversation_id"):
                    print(f"更新用户的 conversation_id: {response['conversation_id']}")
                    update_request = UpdateUserRequest(
                        userNickName=user_info.userNickName,
                        aiAgentName=user_info.aiAgentName,
                        agentId=response["conversation_id"]
                    )
                    await self.user_service.update_user(user_id, update_request)
                    print("用户信息更新成功")
                
                answer = response.get("answer", "")
                print(f"获取到回答: {answer}")
                
                print("开始保存助手回复")
                assistant_message = ChatMessage(
                    user_id=user_id,
                    role="assistant",
                    content=answer,
                    agent_name=user_info.aiAgentName,
                    created_at=current_time  # 修改为 created_at
                )
                await self.chat_repository.save_message(assistant_message)
                print("助手回复保存成功")
                
                return answer
            else:
                # Original OpenAI logic
                messages = [{"role": "user", "content": message}]
                completion = self.client.chat.completions.create(
                    model="yi-34b-chat",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=150
                )
                answer = completion.choices[0].message.content
                
                # 保存助手回复
                assistant_message = ChatMessage(
                    user_id=user_id,
                    role="assistant",
                    content=answer,
                    agent_name=user_info.aiAgentName,
                    created_at=datetime.now().isoformat()  # 添加 created_at
                )
                await self.chat_repository.save_message(assistant_message)
                
                return answer

        except Exception as e:
            print(f"生成回复过程中出错: {str(e)}")
            raise

    @staticmethod
    async def get_chat_history(
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ChatHistoryItem], int]:
        chat_collection = MongoDB.get_collection("chat_messages")
        
        # 构建查询条件，添加 created_at 字段存在性检查
        query = {
            "user_id": user_id,
            "created_at": {"$exists": True}  # 只查询包含 created_at 字段的记录
        }
        
        if start_time:
            query["created_at"]["$gte"] = start_time.isoformat()
        if end_time:
            query["created_at"]["$lte"] = end_time.isoformat()
                
        # 获取总记录数
        total = await chat_collection.count_documents(query)
        
        # 计算分页
        skip = (page - 1) * page_size
        
        # 获取指定页的记录
        cursor = chat_collection.find(query)
        cursor.sort("created_at", -1)  # 使用 created_at 排序
        cursor.skip(skip).limit(page_size)
        
        history = []
        async for doc in cursor:
            # Convert datetime to ISO format string if needed
            created_at = doc["created_at"]
            if isinstance(created_at, datetime):
                created_at = created_at.isoformat()
                
            history.append(ChatHistoryItem(
                role=doc["role"],
                content=doc["content"],
                timestamp=created_at  # Now it's guaranteed to be a string
            ).model_dump())
            
        return history, total

    async def get_user(self, user_id: str) -> Optional[UserInfo]:  # Add self parameter
        user_info = await self.user_service.get_user(user_id)
        if not user_info:
            raise ValueError("User not found")
            
        # 确保包含 createdTime 字段
        if not hasattr(user_info, 'createdTime'):
            user_info.createdTime = int(time.time() * 1000)  # 使用当前时间戳作为默认值
            
        return user_info