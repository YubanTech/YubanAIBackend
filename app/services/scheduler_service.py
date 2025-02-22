from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from typing import Any, Coroutine

from abc import ABC, abstractmethod

class SchedulerService(ABC):
    """定时任务调度服务抽象基类"""
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._init_scheduler()
        
    def _init_scheduler(self):
        """初始化调度器基础配置"""
        self.scheduler.configure(timezone=pytz.timezone('Asia/Shanghai'))
        self._add_base_jobs()
        
    @abstractmethod
    def _add_base_jobs(self):
        """添加基础定时任务（由子类实现）"""
        pass
        
    def add_daily_job(self, 
                     func: Coroutine[Any, Any, None], 
                     hour: int = 6,
                     minute: int = 0) -> None:
        """添加每日定时任务
        Args:
            func: 要执行的异步函数
            hour: 小时（24小时制）
            minute: 分钟
        """
        self.scheduler.add_job(
            func,
            'cron', 
            hour=hour,
            minute=minute
        )
        
    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
