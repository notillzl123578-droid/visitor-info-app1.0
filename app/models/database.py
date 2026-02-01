"""简化的数据库管理模块"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """简化的数据库管理类"""
    
    def __init__(self, db_path='data/app.db'):
        """初始化数据库"""
        self.db_path = db_path
        
        # 确保data目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 简单的数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT,
                exported BOOLEAN DEFAULT 0
            )
        ''')
        
        # 导出历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                filename TEXT,
                file_path TEXT,
                row_count INTEGER,
                activity_data TEXT,
                guests_data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_current_session(self, activity: dict, guests: list):
        """保存数据 - 简化版本，避免重复"""
        if not guests:  # 如果没有来宾数据，不保存
            print("⚠️ 没有来宾数据，跳过保存")
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查是否已存在相同数据（不包含时间戳）
        check_data = {
            'activity': activity,
            'guests': guests
        }
        check_json = json.dumps(check_data, ensure_ascii=False, sort_keys=True)
        
        cursor.execute('''
            SELECT data_json FROM visitor_data WHERE exported = 0
        ''')
        
        existing_records = cursor.fetchall()
        for record in existing_records:
            existing_data = json.loads(record[0])
            existing_check = {
                'activity': existing_data.get('activity', {}),
                'guests': existing_data.get('guests', [])
            }
            existing_check_json = json.dumps(existing_check, ensure_ascii=False, sort_keys=True)
            
            if check_json == existing_check_json:
                print("⚠️ 相同数据已存在，跳过重复保存")
                conn.close()
                return
        
        # 构建数据（包含时间戳）
        data = {
            'activity': activity,
            'guests': guests,
            'saved_at': datetime.now().isoformat()
        }
        
        # 保存数据
        cursor.execute('''
            INSERT INTO visitor_data (data_json, exported)
            VALUES (?, 0)
        ''', (json.dumps(data, ensure_ascii=False),))
        
        conn.commit()
        conn.close()
        print(f'✓ 数据已保存，{len(guests)}位来宾')
    
    def load_current_session(self) -> Optional[Dict]:
        """加载当前数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data_json FROM visitor_data 
            WHERE exported = 0
            ORDER BY created_at ASC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
        
        # 合并所有批次
        all_batches = []
        for row in rows:
            data = json.loads(row[0])
            all_batches.append(data)
        
        return {'batches': all_batches}
    
    def clear_current_session(self):
        """清空当前数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE visitor_data SET exported = 1 WHERE exported = 0')
        
        conn.commit()
        conn.close()
        print('✓ 数据已清空')
    
    def add_export_history(self, filename: str, file_path: str, row_count: int, batches_data: list):
        """添加导出历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO export_history 
            (filename, file_path, row_count, activity_data, guests_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            filename,
            file_path,
            row_count,
            json.dumps(batches_data, ensure_ascii=False),
            json.dumps({'total_batches': len(batches_data)}, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        print(f'✓ 已添加历史记录: {filename}')
    
    def get_export_history(self, limit=50):
        """获取导出历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, exported_at, filename, file_path, row_count
            FROM export_history
            ORDER BY exported_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'exported_at': row[1],
                'filename': row[2],
                'file_path': row[3],
                'row_count': row[4]
            })
        
        return history
    
    def delete_history_record(self, record_id: int):
        """删除历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM export_history WHERE id = ?', (record_id,))
        
        conn.commit()
        conn.close()
        print(f'✓ 已删除历史记录 ID: {record_id}')
    
    def get_statistics(self):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总导出次数
        cursor.execute('SELECT COUNT(*) FROM export_history')
        total_exports = cursor.fetchone()[0]
        
        # 总数据条数
        cursor.execute('SELECT SUM(row_count) FROM export_history')
        total_rows = cursor.fetchone()[0] or 0
        
        # 当前未导出数据
        data = self.load_current_session()
        if data and 'batches' in data:
            current_count = sum(len(batch.get('guests', [])) for batch in data['batches'])
        else:
            current_count = 0
        
        conn.close()
        
        return {
            'total_exports': total_exports,
            'total_rows': total_rows,
            'current_count': current_count
        }

