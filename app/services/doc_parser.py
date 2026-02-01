"""旧版Word文档(.doc)解析器"""
import os
import tempfile
from typing import Tuple, List
from app.models import GuestInfo


class DocParser:
    """旧版Word文档解析器（使用pywin32）"""
    
    def __init__(self):
        """初始化解析器"""
        self.word_app = None
    
    def parse_doc(self, file_path: str) -> Tuple[str, List[GuestInfo]]:
        """
        解析.doc文件
        
        Args:
            file_path: .doc文件路径
            
        Returns:
            (文本内容, 来宾信息列表)
        """
        try:
            import win32com.client
            
            # 创建Word应用
            if not self.word_app:
                self.word_app = win32com.client.Dispatch("Word.Application")
                self.word_app.Visible = False
            
            # 打开文档
            doc = self.word_app.Documents.Open(os.path.abspath(file_path))
            
            # 提取文本
            text = doc.Content.Text
            
            # 提取表格数据
            guests = self._extract_tables(doc)
            
            # 关闭文档
            doc.Close(False)
            
            return text, guests
            
        except ImportError:
            print('警告: pywin32未安装，无法解析.doc文件')
            print('请运行: pip install pywin32')
            return '', []
        except Exception as e:
            print(f'解析.doc文件失败: {e}')
            return '', []
    
    def _extract_tables(self, doc) -> List[GuestInfo]:
        """从Word文档中提取表格数据"""
        guests = []
        
        try:
            # 遍历所有表格
            for table in doc.Tables:
                # 检查是否是来宾信息表（至少6列）
                if table.Columns.Count < 6:
                    continue
                
                # 跳过表头（第一行）
                for row_idx in range(2, table.Rows.Count + 1):
                    try:
                        row = table.Rows(row_idx)
                        
                        # 提取数据（6列格式：序号 | 来宾单位 | 姓名 | 民族 | 职务 | 健康状况）
                        company = row.Cells(2).Range.Text.strip().replace('\r\x07', '')
                        name = row.Cells(3).Range.Text.strip().replace('\r\x07', '')
                        position = row.Cells(5).Range.Text.strip().replace('\r\x07', '')
                        
                        # 过滤空行和表头
                        if name and name not in ['姓名', '']:
                            guest = GuestInfo(
                                company=company,
                                name=name,
                                position=position
                            )
                            guests.append(guest)
                    
                    except Exception as e:
                        # 跳过无效行
                        continue
        
        except Exception as e:
            print(f'提取表格失败: {e}')
        
        return guests
    
    def close(self):
        """关闭Word应用"""
        if self.word_app:
            try:
                self.word_app.Quit()
                self.word_app = None
            except:
                pass
    
    def __del__(self):
        """析构函数"""
        self.close()
