"""历史记录界面"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from app.models import Database


class HistoryScreen(Screen):
    """历史记录界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = Database()
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        # 设置背景色
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题栏
        title_layout = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        back_btn = Button(
            text='← 返回',
            size_hint_x=0.2,
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        back_btn.bind(on_press=self.go_back)
        title_layout.add_widget(back_btn)
        
        title = Label(
            text='导出历史记录',
            font_size='24sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            bold=True,
            color=(0.2, 0.4, 0.8, 1)
        )
        title_layout.add_widget(title)
        
        refresh_btn = Button(
            text='🔄 刷新',
            size_hint_x=0.2,
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.6, 1, 1)
        )
        refresh_btn.bind(on_press=self.refresh_history)
        title_layout.add_widget(refresh_btn)
        
        layout.add_widget(title_layout)
        
        # 统计信息
        self.stats_label = Label(
            text='',
            size_hint_y=None,
            height=40,
            font_size='14sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(self.stats_label)
        
        # 历史记录列表
        scroll = ScrollView()
        self.history_list = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=[10, 10]
        )
        self.history_list.bind(minimum_height=self.history_list.setter('height'))
        scroll.add_widget(self.history_list)
        
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _update_bg(self, instance, value):
        """更新背景"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_enter(self):
        """进入界面时刷新"""
        self.refresh_history()
    
    def refresh_history(self, instance=None):
        """刷新历史记录 - 完整版本"""
        # 清空列表
        self.history_list.clear_widgets()
        
        # 获取统计信息
        try:
            stats = self.database.get_statistics()
            self.stats_label.text = (
                f"总导出次数: {stats['total_exports']} | "
                f"总数据条数: {stats['total_rows']} | "
                f"当前未导出: {stats['current_count']}条"
            )
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            self.stats_label.text = "统计信息加载失败"
        
        # 获取历史记录
        try:
            history = self.database.get_export_history(limit=50)
            
            if not history:
                no_data_label = Label(
                    text='暂无历史记录',
                    font_size='16sp',
                    font_name='C:/Windows/Fonts/msyh.ttc',
                    color=(0.6, 0.6, 0.6, 1),
                    size_hint_y=None,
                    height=100
                )
                self.history_list.add_widget(no_data_label)
                return
            
            # 显示历史记录
            for record in history:
                record_widget = self.create_record_widget(record)
                self.history_list.add_widget(record_widget)
                
        except Exception as e:
            print(f"获取历史记录失败: {e}")
            error_label = Label(
                text=f'历史记录加载失败: {str(e)}',
                font_size='16sp',
                font_name='C:/Windows/Fonts/msyh.ttc',
                color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=100
            )
            self.history_list.add_widget(error_label)
    
    def create_record_widget(self, record: dict):
        """创建历史记录卡片"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=[15, 10],
            spacing=5
        )
        
        # 添加背景
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
        
        def update_card_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        card.bind(pos=update_card_bg, size=update_card_bg)
        
        # 文件名
        filename_label = Label(
            text=f"📊 {record['filename']}",
            size_hint_y=None,
            height=30,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            bold=True
        )
        filename_label.bind(size=filename_label.setter('text_size'))
        card.add_widget(filename_label)
        
        # 详细信息
        info_label = Label(
            text=f"导出时间: {record['exported_at']} | 数据条数: {record['row_count']}",
            size_hint_y=None,
            height=25,
            font_size='12sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.5, 0.5, 0.5, 1),
            halign='left'
        )
        info_label.bind(size=info_label.setter('text_size'))
        card.add_widget(info_label)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        open_btn = Button(
            text='打开文件',
            font_size='12sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.6, 1, 1)
        )
        open_btn.bind(on_press=lambda x: self.open_file(record['file_path']))
        btn_layout.add_widget(open_btn)
        
        delete_btn = Button(
            text='删除',
            font_size='12sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.9, 0.4, 0.4, 1)
        )
        delete_btn.bind(on_press=lambda x: self.delete_record(record['id']))
        btn_layout.add_widget(delete_btn)
        
        card.add_widget(btn_layout)
        
        return card
    
    def open_file(self, file_path: str):
        """打开文件"""
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)
            except Exception as e:
                self.show_message('错误', f'无法打开文件: {e}')
        else:
            self.show_message('错误', '文件不存在')
    
    def delete_record(self, record_id: int):
        """删除记录"""
        # 确认对话框
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text='确定要删除这条记录吗？',
            font_name='C:/Windows/Fonts/msyh.ttc'
        ))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        confirm_btn = Button(
            text='确定',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.9, 0.4, 0.4, 1)
        )
        cancel_btn = Button(
            text='取消',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='确认删除',
            content=content,
            size_hint=(0.7, 0.3)
        )
        
        def on_confirm(instance):
            self.database.delete_history_record(record_id)
            popup.dismiss()
            self.refresh_history()
            self.show_message('成功', '记录已删除')
        
        def on_cancel(instance):
            popup.dismiss()
        
        confirm_btn.bind(on_press=on_confirm)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def go_back(self, instance):
        """返回主界面"""
        self.manager.current = 'main'
    
    def show_message(self, title: str, message: str):
        """显示消息"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            font_name='C:/Windows/Fonts/msyh.ttc'
        ))
        
        btn = Button(
            text='确定',
            size_hint_y=None,
            height=50,
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.6, 1, 1)
        )
        content.add_widget(btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.3)
        )
        
        btn.bind(on_press=popup.dismiss)
        popup.open()
