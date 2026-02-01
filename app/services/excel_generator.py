"""简化的Excel生成器"""
import csv
import os
from datetime import datetime
from pathlib import Path


class ExcelGenerator:
    """简化的Excel生成器"""
    
    @staticmethod
    def generate_csv(activity=None, guests=None, existing_data=None, 
                     output_path=None, batches_data=None) -> str:
        """生成CSV文件 - 简化版本"""
        
        if output_path is None:
            documents_dir = Path.home() / "Documents"
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = documents_dir / f'visitor_data_{timestamp}.csv'
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([
                '日期', '参观事项', '陪同领导', '陪同部门', '参观路线',
                '来宾单位', '姓名', '职务', '人数'
            ])
            
            # 处理批次数据
            if batches_data:
                for batch in batches_data:
                    activity_info = batch.get('activity', {})
                    guest_list = batch.get('guests', [])
                    
                    if guest_list:
                        guest_count = len(guest_list)
                        for i, guest in enumerate(guest_list):
                            # 只在第一行显示人数
                            count = str(guest_count) if i == 0 else ''
                            
                            writer.writerow([
                                activity_info.get('date', ''),
                                activity_info.get('event', ''),
                                activity_info.get('leader', ''),
                                activity_info.get('department', ''),
                                activity_info.get('route', '').replace('\\n', ' '),
                                guest.get('company', ''),
                                guest.get('name', ''),
                                guest.get('position', ''),
                                count
                            ])
        
        print(f'CSV文件生成成功: {output_path}')
        return str(output_path)
