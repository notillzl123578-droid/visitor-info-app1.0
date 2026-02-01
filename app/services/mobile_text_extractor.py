"""移动版文本提取器 - 简化版本"""
import re
from typing import Dict, List, Tuple


class MobileTextExtractor:
    """移动版文本提取器"""
    
    def __init__(self):
        """初始化提取器"""
        pass
    
    def extract_from_text(self, text: str) -> Tuple[Dict, List[Dict]]:
        """从文本中提取活动信息和来宾信息"""
        activity = self.extract_activity_info(text)
        guests = self.extract_guest_info(text)
        return activity, guests
    
    def extract_activity_info(self, text: str) -> Dict:
        """提取活动信息"""
        activity = {}
        
        # 提取日期
        date_match = re.search(r'(\d{1,2}月\d{1,2}日)', text)
        if date_match:
            activity['date'] = date_match.group(1)
        
        # 提取参观事项
        event_match = re.search(r'\d{1,2}月\d{1,2}日(?:（[^）]+）)?\s*([^\n。]+?)(?:调研时间|参观时间|陪同|车辆|路线|\n|。|$)', text)
        if event_match:
            activity['event'] = event_match.group(1).strip()
        
        # 提取陪同领导
        leader_match = re.search(r'陪同领导[：:]\s*([^\n]+?)(?:陪同部门|车辆|路线|\n|$)', text)
        if leader_match:
            activity['leader'] = leader_match.group(1).strip()
        
        # 提取陪同部门
        dept_match = re.search(r'陪同部门[：:]\s*([^\n]+?)(?:车辆|路线|\n|$)', text)
        if dept_match:
            activity['department'] = dept_match.group(1).strip()
        
        # 提取参观路线
        route_match = re.search(r'(?:调研|参观)?路线[：:]\s*([^\n]+(?:\n(?!具体要求|任务分工|一、|二、)[^\n]+)*)', text)
        if route_match:
            activity['route'] = route_match.group(1).strip()
        
        return activity
    
    def extract_guest_info(self, text: str) -> List[Dict]:
        """提取来宾信息"""
        guests = []
        lines = text.split('\n')
        in_table = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                if in_table:
                    in_table = False
                continue
            
            # 检测表头
            if self._is_table_header(line):
                in_table = True
                continue
            
            # 提取表格数据
            if in_table and line:
                # 跳过分隔线
                if re.match(r'^[-=\s]+$', line):
                    continue
                
                guest = self._parse_guest_line(line)
                if guest and self._is_valid_guest(guest, guests):
                    guests.append(guest)
            
            # 结束表格提取的条件
            if line.startswith(('具体要求', '任务分工')) or re.match(r'^[一二三四五六七八九十]+、', line):
                in_table = False
        
        return guests
    
    def _is_table_header(self, line: str) -> bool:
        """检测是否为表头"""
        return (('序号' in line or '序' in line or '号' in line or '来宾' in line or '单位' in line) and 
                ('姓名' in line or '名' in line or '职务' in line))
    
    def _parse_guest_line(self, line: str) -> Dict:
        """解析来宾信息行"""
        cells = []
        
        # 尝试多种分隔符
        if '\t' in line:
            cells = line.split('\t')
        elif re.search(r'\s{2,}', line):
            cells = re.split(r'\s{2,}', line)
        elif '|' in line or '｜' in line:
            cells = re.split(r'[|｜]', line)
            cells = [c for c in cells if c.strip()]
        else:
            cells = line.split()
        
        cells = [c.strip() for c in cells if c.strip() and c.strip() not in ['|', '｜']]
        
        if not cells:
            return None
        
        # 判断第一列是否是序号
        has_seq_no = re.match(r'^\d+[°º]?$', cells[0])
        start_index = 1 if has_seq_no else 0
        
        guest = None
        
        # 根据列数判断格式
        if len(cells) >= start_index + 5:
            # 6列格式：序号、来宾单位、姓名、民族、职务、健康状况
            guest = {
                'company': cells[start_index] or '',
                'name': cells[start_index + 1] or '',
                'position': cells[start_index + 3] or ''  # 跳过民族，取职务
            }
        elif len(cells) >= start_index + 4:
            # 5列格式：序号、来宾单位、姓名、民族、职务
            guest = {
                'company': cells[start_index] or '',
                'name': cells[start_index + 1] or '',
                'position': cells[start_index + 3] or ''  # 跳过民族，取职务
            }
        elif len(cells) >= start_index + 3:
            # 4列格式：序号、来宾单位、姓名、职务
            guest = {
                'company': cells[start_index] or '',
                'name': cells[start_index + 1] or '',
                'position': cells[start_index + 2] or ''
            }
        
        return guest
    
    def _is_valid_guest(self, guest: Dict, existing_guests: List[Dict]) -> bool:
        """检查来宾信息是否有效"""
        if not guest or not guest.get('name'):
            return False
        
        # 检查姓名长度和内容
        name = guest['name']
        if len(name) < 2 or '姓名' in name or '序号' in name:
            return False
        
        # 检查是否重复
        for existing in existing_guests:
            if existing['name'] == name and existing['company'] == guest['company']:
                return False
        
        return True