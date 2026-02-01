"""数据模型"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class ActivityInfo:
    """活动信息"""
    date: str = ''  # 日期
    event: str = ''  # 参观事项
    leader: str = ''  # 陪同领导
    department: str = ''  # 陪同部门
    route: str = ''  # 参观路线


@dataclass
class GuestInfo:
    """来宾信息"""
    company: str = ''  # 来宾单位
    name: str = ''  # 姓名
    position: str = ''  # 职务


@dataclass
class ExtractedData:
    """提取的数据"""
    activity: ActivityInfo = field(default_factory=ActivityInfo)
    guests: List[GuestInfo] = field(default_factory=list)
    existing_data: List[dict] = field(default_factory=list)
    
    @property
    def total_count(self) -> int:
        """总人数"""
        return len(self.guests)
