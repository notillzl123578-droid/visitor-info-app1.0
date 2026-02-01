"""文本信息提取器"""
import re
from typing import List
from app.models import ActivityInfo, GuestInfo


class TextExtractor:
    """文本信息提取器 - 提取活动信息和来宾信息"""
    
    def __init__(self):
        self.activity = ActivityInfo()
    
    def extract_activity_info(self, text: str, existing_activity: ActivityInfo = None) -> ActivityInfo:
        """
        从文本中提取活动信息
        采用累积策略：只在字段为空时才填充
        """
        if existing_activity:
            self.activity = existing_activity
        else:
            self.activity = ActivityInfo()
        
        print(f'开始提取活动信息，文本长度: {len(text)}')
        
        # 提取日期（A列）- 匹配"X月X日"
        if not self.activity.date:
            date_match = re.search(r'(\d{1,2}月\d{1,2}日)', text)
            if date_match:
                self.activity.date = date_match.group(1)
                print(f'提取日期: {self.activity.date}')
        
        # 提取参观事项（B列）- 改进提取逻辑
        if not self.activity.event:
            # 方法1：提取日期后面紧跟的内容，包含"参观"、"到公司"等关键词
            event_patterns = [
                # 匹配"1月29日(周四)燕山石化客人到公司参观"这种格式
                r'\d{1,2}月\d{1,2}日(?:\([^)]+\))?\s*([^。\n]*?(?:客人到公司参观|到公司参观|客人参观|参观|调研|来访)[^。\n]*?)(?:\s*参观时间|调研时间|陪同|车辆|路线|\n|。|$)',
                # 匹配包含关键词的完整句子
                r'([^。\n]*?(?:客人到公司参观|到公司参观|石化客人|客人|参观|调研|来访)[^。\n]*?)(?:\s*参观时间|调研时间|陪同|车辆|路线|\n|。|$)',
                # 匹配日期后的内容
                r'\d{1,2}月\d{1,2}日(?:\([^)]+\))?\s*([^。\n]+?)(?:\s*参观时间|调研时间|陪同|车辆|路线|\n|。|$)'
            ]
            
            for pattern in event_patterns:
                event_match = re.search(pattern, text)
                if event_match:
                    event_text = event_match.group(1).strip()
                    # 清理多余的符号和空格
                    event_text = re.sub(r'^[：:：\s]+', '', event_text)
                    event_text = re.sub(r'[：:：\s]+$', '', event_text)
                    # 特殊处理：如果包含"客人到公司参观"，确保完整提取
                    if '客人到公司参观' in event_text or '石化客人' in event_text:
                        # 提取包含关键信息的完整描述
                        full_match = re.search(r'([^。\n]*?(?:石化|客人)[^。\n]*?(?:到公司参观|参观)[^。\n]*?)', text)
                        if full_match:
                            event_text = full_match.group(1).strip()
                    
                    if len(event_text) > 3:  # 确保不是太短的内容
                        self.activity.event = event_text
                        print(f'提取参观事项: {self.activity.event}')
                        break
        
        # 提取陪同领导（C列）
        if not self.activity.leader:
            leader_match = re.search(r'陪同领导[：:]\s*([^\n]+?)(?:陪同部门|陪同单位|车辆|路线|\n|$)', text)
            if leader_match:
                self.activity.leader = leader_match.group(1).strip()
                print(f'提取陪同领导: {self.activity.leader}')
        
        # 提取陪同部门（D列）
        if not self.activity.department:
            dept_match = re.search(r'陪同(?:部门|单位)[：:]\s*([^\n]+?)(?:车辆|路线|\n|$)', text)
            if dept_match:
                self.activity.department = dept_match.group(1).strip()
                print(f'提取陪同部门: {self.activity.department}')
        
        # 提取参观路线（E列）- 模糊查找包含"路线"的内容
        if not self.activity.route:
            route_match = re.search(
                r'(?:调研|参观)?路线[：:]\s*([^\n]+(?:\n(?!具体要求|任务分工|一、|二、|序号)[^\n]+)*)',
                text
            )
            if route_match:
                self.activity.route = route_match.group(1).strip()
                print(f'提取参观路线: {self.activity.route}')
        
        print(f'提取完成: {self.activity}')
        return self.activity
    
    def extract_guests_from_text(self, text: str) -> List[GuestInfo]:
        """
        从文本中提取来宾信息
        支持表格格式的文本
        """
        guests = []
        
        print(f'开始从文本提取来宾信息，文本长度: {len(text)}')
        
        # 查找表格格式的数据
        # 格式1: 序号\t来宾单位\t姓名\t民族\t职务\t健康状况
        # 格式2: 序号 来宾单位 姓名 民族 职务 健康状况
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 跳过表头
            if '序号' in line or '来宾单位' in line or '姓名' in line:
                print(f'跳过表头: {line}')
                continue
            
            # 尝试用制表符分割
            parts = re.split(r'\t+', line)
            if len(parts) < 3:
                # 尝试用空格分割
                parts = re.split(r'\s{2,}', line)
            
            if len(parts) < 3:
                continue
            
            # 判断第一列是否是序号
            has_seq_no = re.match(r'^\d+[°º]?$', parts[0].strip())
            start_index = 1 if has_seq_no else 0
            
            # 提取来宾信息
            if len(parts) >= start_index + 3:
                company = parts[start_index].strip() if start_index < len(parts) else ''
                name = parts[start_index + 1].strip() if start_index + 1 < len(parts) else ''
                
                # 职务在第4列（跳过民族）或第3列
                if len(parts) >= start_index + 5:
                    # 6列格式：序号、来宾单位、姓名、民族、职务、健康状况
                    position = parts[start_index + 3].strip() if start_index + 3 < len(parts) else ''
                elif len(parts) >= start_index + 4:
                    # 5列格式：序号、来宾单位、姓名、民族、职务
                    position = parts[start_index + 3].strip() if start_index + 3 < len(parts) else ''
                else:
                    # 4列格式：序号、来宾单位、姓名、职务
                    position = parts[start_index + 2].strip() if start_index + 2 < len(parts) else ''
                
                # 验证数据有效性
                if name and len(name) >= 2 and '姓名' not in name:
                    guest = GuestInfo(
                        company=company,
                        name=name,
                        position=position
                    )
                    
                    # 避免重复
                    if not any(g.name == guest.name and g.company == guest.company for g in guests):
                        guests.append(guest)
                        print(f'✓ 提取来宾: {company} - {name} - {position}')
        
        print(f'共提取来宾: {len(guests)}位')
        return guests
