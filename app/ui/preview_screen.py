"""预览界面 - 数据编辑和导出"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from app.models import ExtractedData, GuestInfo
from app.services import ExcelGenerator


class PreviewScreen(Screen):
    """预览界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = ExtractedData()
        self.excel_generator = ExcelGenerator()
        self.activity_inputs = {}
        self.guest_inputs = []
        self.build_ui()
    
    def build_ui(self):
        """构建UI"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        title_layout = BoxLayout(size_hint_y=None, height=50)
        title = Label(
            text='数据预览与编辑',
            font_size='20sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            bold=True
        )
        title_layout.add_widget(title)
        
        self.count_label = Label(
            text='总人数: 0',
            size_hint_x=0.3,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc'
        )
        title_layout.add_widget(self.count_label)
        main_layout.add_widget(title_layout)
        
        # 滚动区域
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # 活动信息区域
        activity_section = self.create_activity_section()
        content.add_widget(activity_section)
        
        # 来宾信息区域
        self.guest_section = BoxLayout(
            orientation='vertical',
            spacing=15,  # 增加来宾之间的间距
            size_hint_y=None
        )
        self.guest_section.bind(minimum_height=self.guest_section.setter('height'))
        content.add_widget(self.guest_section)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # 底部按钮
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        add_guest_btn = Button(
            text='添加来宾',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.5, 0.7, 0.9, 1),
            on_press=self.add_guest
        )
        btn_layout.add_widget(add_guest_btn)
        
        save_btn = Button(
            text='💾 保存',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.8, 0.5, 1),
            on_press=self.save_and_return
        )
        btn_layout.add_widget(save_btn)
        
        export_btn = Button(
            text='导出Excel',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.6, 1, 1),
            on_press=self.export_excel
        )
        btn_layout.add_widget(export_btn)
        
        back_btn = Button(
            text='返回',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.7, 0.7, 0.7, 1),
            on_press=self.go_back
        )
        btn_layout.add_widget(back_btn)
        
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)
    
    def create_activity_section(self):
        """创建活动信息区域"""
        section = BoxLayout(
            orientation='vertical',
            spacing=8,
            size_hint_y=None,
            height=480,  # 460 + 20 (增加总高度以适应更大的字段)
            padding=[10, 10]
        )
        
        # 添加背景色
        with section.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.95, 1, 0.95, 1)  # 淡绿色背景
            section.bg_rect = RoundedRectangle(pos=section.pos, size=section.size, radius=[10])
        
        def update_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        section.bind(pos=update_bg, size=update_bg)
        
        # 标题
        title = Label(
            text='━━━ 活动信息 ━━━',
            size_hint_y=None,
            height=35,
            font_size='18sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            bold=True,
            color=(0.2, 0.6, 0.2, 1)
        )
        section.add_widget(title)
        
        fields = [
            ('date', '日期'),
            ('event', '参观事项'),
            ('leader', '陪同领导'),
            ('department', '陪同部门'),
            ('route', '参观路线')
        ]
        
        for field_name, label_text in fields:
            # 根据字段类型调整高度 - 增加4个单位让文字完全可见
            if field_name == 'route':
                field_height = 116  # 112 + 4
            else:
                field_height = 66  # 62 + 4
            
            field_layout = BoxLayout(size_hint_y=None, height=field_height, spacing=5)
            
            label = Label(
                text=label_text + ':',
                size_hint_x=0.25,
                font_name='C:/Windows/Fonts/msyh.ttc',
                font_size='15sp',
                color=(0.3, 0.3, 0.3, 1),
                halign='right',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            field_layout.add_widget(label)
            
            text_input = TextInput(
                multiline=(field_name == 'route'),
                size_hint_x=0.75,
                font_name='C:/Windows/Fonts/msyh.ttc',
                font_size='14sp',
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1),
                padding=[12, 12, 12, 12]
            )
            self.activity_inputs[field_name] = text_input
            field_layout.add_widget(text_input)
            
            section.add_widget(field_layout)
        
        return section
    
    def create_guest_row(self, guest: GuestInfo, index: int):
        """创建来宾信息行"""
        row = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=190,  # 178 + 12 (增加总高度以适应更大的字段)
            padding=[10, 10]
        )
        
        # 添加背景色区分
        with row.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.95, 0.97, 1, 1)  # 淡蓝色背景
            row.bg_rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[10])
        
        def update_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        row.bind(pos=update_bg, size=update_bg)
        
        # 标题行
        title_row = BoxLayout(size_hint_y=None, height=35, spacing=10)
        title_label = Label(
            text=f'━━━ 来宾 {index + 1} ━━━',
            font_name='C:/Windows/Fonts/msyh.ttc',
            font_size='16sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1)
        )
        title_row.add_widget(title_label)
        
        delete_btn = Button(
            text='✕ 删除',
            size_hint_x=0.25,
            font_name='C:/Windows/Fonts/msyh.ttc',
            font_size='14sp',
            background_color=(0.9, 0.3, 0.3, 1),
            on_press=lambda x: self.delete_guest(index)
        )
        title_row.add_widget(delete_btn)
        row.add_widget(title_row)
        
        # 输入字段
        guest_inputs = {}
        
        for field_name, label_text in [('company', '来宾单位'), ('name', '姓名'), ('position', '职务')]:
            field_layout = BoxLayout(size_hint_y=None, height=51, spacing=5)  # 47 + 4
            
            label = Label(
                text=label_text + ':',
                size_hint_x=0.25,
                font_name='C:/Windows/Fonts/msyh.ttc',
                font_size='14sp',
                color=(0.3, 0.3, 0.3, 1),
                halign='right',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            field_layout.add_widget(label)
            
            text_input = TextInput(
                text=getattr(guest, field_name, ''),
                size_hint_x=0.75,
                font_name='C:/Windows/Fonts/msyh.ttc',
                font_size='14sp',
                multiline=False,
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1),
                padding=[12, 8, 12, 8]
            )
            guest_inputs[field_name] = text_input
            field_layout.add_widget(text_input)
            
            row.add_widget(field_layout)
        
        self.guest_inputs.append(guest_inputs)
        return row
    
    def load_data(self, data: ExtractedData):
        """加载数据"""
        self.data = data
        
        # 加载活动信息
        self.activity_inputs['date'].text = data.activity.date
        self.activity_inputs['event'].text = data.activity.event
        self.activity_inputs['leader'].text = data.activity.leader
        self.activity_inputs['department'].text = data.activity.department
        self.activity_inputs['route'].text = data.activity.route
        
        # 加载来宾信息
        self.guest_inputs = []
        self.guest_section.clear_widgets()
        
        for i, guest in enumerate(data.guests):
            guest_row = self.create_guest_row(guest, i)
            self.guest_section.add_widget(guest_row)
        
        # 更新总人数
        self.count_label.text = f'总人数: {data.total_count}'
    
    def add_guest(self, instance):
        """添加来宾"""
        new_guest = GuestInfo()
        self.data.guests.append(new_guest)
        
        index = len(self.data.guests) - 1
        guest_row = self.create_guest_row(new_guest, index)
        self.guest_section.add_widget(guest_row)
        
        self.count_label.text = f'总人数: {self.data.total_count}'
    
    def delete_guest(self, index: int):
        """删除来宾"""
        if 0 <= index < len(self.data.guests):
            self.data.guests.pop(index)
            self.guest_inputs.pop(index)
            
            # 重新构建来宾列表
            self.guest_section.clear_widgets()
            self.guest_inputs = []
            
            for i, guest in enumerate(self.data.guests):
                guest_row = self.create_guest_row(guest, i)
                self.guest_section.add_widget(guest_row)
            
            self.count_label.text = f'总人数: {self.data.total_count}'
    
    def save_and_return(self, instance):
        """保存数据并返回主页"""
        # 更新数据
        self.data.activity.date = self.activity_inputs['date'].text
        self.data.activity.event = self.activity_inputs['event'].text
        self.data.activity.leader = self.activity_inputs['leader'].text
        self.data.activity.department = self.activity_inputs['department'].text
        self.data.activity.route = self.activity_inputs['route'].text
        
        for i, guest_input in enumerate(self.guest_inputs):
            if i < len(self.data.guests):
                self.data.guests[i].company = guest_input['company'].text
                self.data.guests[i].name = guest_input['name'].text
                self.data.guests[i].position = guest_input['position'].text
        
        # 保存到数据库（累积模式）
        from app.models import Database
        database = Database()
        
        activity_dict = {
            'date': self.data.activity.date,
            'event': self.data.activity.event,
            'leader': self.data.activity.leader,
            'department': self.data.activity.department,
            'route': self.data.activity.route
        }
        guests_list = [
            {
                'company': g.company,
                'name': g.name,
                'position': g.position
            }
            for g in self.data.guests
        ]
        
        database.save_current_session(activity_dict, guests_list)
        
        # 显示消息并返回
        guest_count = len(self.data.guests)
        message = f'数据已保存！\n本次: {guest_count}位来宾\n\n可以继续添加更多数据'
        
        self.show_message('保存成功', message, self.go_back_to_main)
    
    def go_back_to_main(self):
        """返回主页并刷新数据显示"""
        main_screen = self.manager.get_screen('main')
        main_screen.refresh_saved_data()
        self.manager.current = 'main'
    
    def export_excel(self, instance):
        """导出Excel"""
        # 更新数据
        self.data.activity.date = self.activity_inputs['date'].text
        self.data.activity.event = self.activity_inputs['event'].text
        self.data.activity.leader = self.activity_inputs['leader'].text
        self.data.activity.department = self.activity_inputs['department'].text
        self.data.activity.route = self.activity_inputs['route'].text
        
        for i, guest_input in enumerate(self.guest_inputs):
            if i < len(self.data.guests):
                self.data.guests[i].company = guest_input['company'].text
                self.data.guests[i].name = guest_input['name'].text
                self.data.guests[i].position = guest_input['position'].text
        
        # 导出Excel
        try:
            from app.services import ExcelGenerator
            from datetime import datetime
            from pathlib import Path
            excel_generator = ExcelGenerator()
            
            # 导出到用户Documents目录，避免权限问题
            documents_dir = Path.home() / "Documents"
            date_str = datetime.now().strftime('%Y-%m-%d')
            output_path = documents_dir / f'visitor_info_{date_str}.csv'
            
            file_path = excel_generator.generate_csv(
                extracted_data.activity,
                extracted_data.guests,
                [],
                str(output_path)
            )
            
            # 添加到历史记录
            import os
            filename = os.path.basename(file_path)
            abs_path = os.path.abspath(file_path)
            
            activity_dict = {
                'date': extracted_data.activity.date,
                'event': extracted_data.activity.event,
                'leader': extracted_data.activity.leader,
                'department': extracted_data.activity.department,
                'route': extracted_data.activity.route
            }
            guests_list = [
                {
                    'company': g.company,
                    'name': g.name,
                    'position': g.position
                }
                for g in extracted_data.guests
            ]
            
            # 导入Database
            from app.models import Database
            database = Database()
            
            database.add_export_history(
                filename=filename,
                file_path=abs_path,
                row_count=len(extracted_data.guests),
                activity=activity_dict,
                guests=guests_list
            )
            
            # 清空当前会话数据
            database.clear_current_session()
            
            message = f'导出成功！\n文件: {filename}\n共{len(extracted_data.guests)}条数据\n\n数据已清空，可开始新的录入'
            
            self.show_message('导出成功', message)
            
        except Exception as e:
            self.show_message('导出失败', f'错误: {str(e)}')
    
    def go_back(self, instance):
        """返回"""
        # 刷新主页显示（即使没有保存，也要显示当前数据库中的数据）
        main_screen = self.manager.get_screen('main')
        main_screen.refresh_saved_data()
        self.manager.current = 'main'
    
    def show_message(self, title: str, message: str, callback=None):
        """显示消息"""
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(
            text=message,
            font_name='C:/Windows/Fonts/msyh.ttc'
        ))
        
        btn = Button(
            text='确定',
            size_hint_y=None,
            height=50,
            font_name='C:/Windows/Fonts/msyh.ttc'
        )
        content.add_widget(btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def on_close(instance):
            popup.dismiss()
            if callback:
                callback()
        
        btn.bind(on_press=on_close)
        popup.open()
