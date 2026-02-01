"""移动版主界面"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform
import os
from app.models.database import Database
from app.services.mobile_text_extractor import MobileTextExtractor


class MobileMainScreen(Screen):
    """移动版主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = Database()
        self.text_extractor = MobileTextExtractor()
        self.current_activity = {}
        self.current_guests = []
        
        # 构建界面
        self.build_ui()
        
        # 刷新数据显示
        Clock.schedule_once(lambda dt: self.refresh_saved_data(), 0.5)
    
    def build_ui(self):
        """构建移动版界面"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text='📱 来宾信息提取工具',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(0.2, 0.4, 0.8, 1)
        )
        main_layout.add_widget(title)
        
        # 滚动区域
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # 文本输入区域
        text_section = self.create_text_section()
        content.add_widget(text_section)
        
        # 文件选择区域
        file_section = self.create_file_section()
        content.add_widget(file_section)
        
        # 已保存数据显示
        self.saved_data_label = Label(
            text='暂无保存的数据',
            text_size=(None, None),
            halign='left',
            valign='top',
            size_hint_y=None,
            height='100dp',
            color=(0.6, 0.6, 0.6, 1)
        )
        content.add_widget(self.saved_data_label)
        
        # 操作按钮
        button_section = self.create_button_section()
        content.add_widget(button_section)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def create_text_section(self):
        """创建文本输入区域"""
        section = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height='200dp')
        
        label = Label(
            text='📝 文本输入',
            font_size='18sp',
            size_hint_y=None,
            height='40dp',
            color=(0.3, 0.3, 0.3, 1)
        )
        section.add_widget(label)
        
        self.text_input = TextInput(
            multiline=True,
            hint_text='请输入或粘贴来宾信息文本...',
            size_hint_y=None,
            height='150dp'
        )
        section.add_widget(self.text_input)
        
        return section
    
    def create_file_section(self):
        """创建文件选择区域"""
        section = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height='80dp')
        
        label = Label(
            text='📁 文件选择',
            font_size='18sp',
            size_hint_y=None,
            height='40dp',
            color=(0.3, 0.3, 0.3, 1)
        )
        section.add_widget(label)
        
        file_button = Button(
            text='📷 选择图片 (OCR识别)',
            size_hint_y=None,
            height='40dp',
            background_color=(0.2, 0.6, 0.9, 1)
        )
        file_button.bind(on_press=self.choose_image)
        section.add_widget(file_button)
        
        return section
    
    def create_button_section(self):
        """创建操作按钮区域"""
        section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height='160dp')
        
        # 处理按钮
        process_btn = Button(
            text='🔄 开始处理',
            size_hint_y=None,
            height='50dp',
            background_color=(0.2, 0.7, 0.3, 1),
            font_size='18sp'
        )
        process_btn.bind(on_press=self.process_data)
        section.add_widget(process_btn)
        
        # 导出按钮
        export_btn = Button(
            text='📊 导出Excel',
            size_hint_y=None,
            height='50dp',
            background_color=(0.8, 0.4, 0.2, 1),
            font_size='18sp'
        )
        export_btn.bind(on_press=self.export_data)
        section.add_widget(export_btn)
        
        # 清空按钮
        clear_btn = Button(
            text='🗑️ 清空数据',
            size_hint_y=None,
            height='50dp',
            background_color=(0.8, 0.2, 0.2, 1),
            font_size='16sp'
        )
        clear_btn.bind(on_press=self.clear_data)
        section.add_widget(clear_btn)
        
        return section
    
    def choose_image(self, instance):
        """选择图片进行OCR识别"""
        if platform == 'android':
            # Android平台使用相机或相册
            self.show_message('提示', 'Android版本暂不支持图片选择\n请使用文本输入功能')
        else:
            # 桌面版本使用文件选择器
            self.show_file_chooser()
    
    def show_file_chooser(self):
        """显示文件选择器"""
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView(
            filters=['*.jpg', '*.jpeg', '*.png', '*.bmp']
        )
        content.add_widget(filechooser)
        
        buttons = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        
        select_btn = Button(text='选择')
        select_btn.bind(on_press=lambda x: self.load_image(filechooser.selection))
        buttons.add_widget(select_btn)
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: self.file_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        content.add_widget(buttons)
        
        self.file_popup = Popup(
            title='选择图片文件',
            content=content,
            size_hint=(0.9, 0.9)
        )
        self.file_popup.open()
    
    def load_image(self, selection):
        """加载选中的图片"""
        if selection:
            self.file_popup.dismiss()
            # 这里应该调用OCR服务，暂时显示提示
            self.show_message('提示', f'已选择图片：{os.path.basename(selection[0])}\n\n移动版暂不支持OCR，请使用文本输入')
    
    def process_data(self, instance):
        """处理数据"""
        text = self.text_input.text.strip()
        if not text:
            self.show_message('提示', '请先输入文本内容')
            return
        
        try:
            # 提取信息
            activity, guests = self.text_extractor.extract_from_text(text)
            
            if not guests:
                self.show_message('提示', '未提取到来宾信息\n请检查文本格式')
                return
            
            # 保存数据
            self.current_activity = activity
            self.current_guests = guests
            
            self.database.save_current_session(activity, guests)
            
            # 清空输入
            self.text_input.text = ''
            
            # 刷新显示
            self.refresh_saved_data()
            
            self.show_message('成功', f'已提取并保存：\n- 活动信息：{len(activity)}项\n- 来宾信息：{len(guests)}位')
            
        except Exception as e:
            self.show_message('错误', f'处理失败：{str(e)}')
    
    def export_data(self, instance):
        """导出数据"""
        try:
            data = self.database.load_current_session()
            if not data or 'batches' not in data or not data['batches']:
                self.show_message('提示', '没有可导出的数据')
                return
            
            from app.services.excel_generator import ExcelGenerator
            
            excel_generator = ExcelGenerator()
            file_path = excel_generator.generate_csv(batches_data=data['batches'])
            
            # 计算总来宾数
            total_guests = sum(len(batch.get('guests', [])) for batch in data['batches'])
            
            # 清空数据
            self.database.clear_current_session()
            self.refresh_saved_data()
            
            filename = os.path.basename(file_path)
            message = f'导出成功！\n文件：{filename}\n共{total_guests}条数据\n\n数据已清空，可开始新的录入'
            self.show_message('导出成功', message)
            
        except Exception as e:
            self.show_message('导出失败', f'错误：{str(e)}')
    
    def clear_data(self, instance):
        """清空数据"""
        # 创建确认对话框
        content = BoxLayout(orientation='vertical', spacing=10)
        
        label = Label(text='确定要清空所有保存的数据吗？\n此操作不可恢复！')
        content.add_widget(label)
        
        buttons = BoxLayout(size_hint_y=None, height='50dp', spacing=10)
        
        confirm_btn = Button(text='确定清空', background_color=(0.8, 0.2, 0.2, 1))
        confirm_btn.bind(on_press=lambda x: self.do_clear_data())
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(text='取消')
        cancel_btn.bind(on_press=lambda x: self.clear_popup.dismiss())
        buttons.add_widget(cancel_btn)
        
        content.add_widget(buttons)
        
        self.clear_popup = Popup(
            title='确认清空',
            content=content,
            size_hint=(0.8, 0.4)
        )
        self.clear_popup.open()
    
    def do_clear_data(self):
        """执行清空数据"""
        self.clear_popup.dismiss()
        self.database.clear_current_session()
        self.refresh_saved_data()
        self.show_message('成功', '数据已清空')
    
    def refresh_saved_data(self):
        """刷新已保存数据显示"""
        try:
            data = self.database.load_current_session()
            
            if data and 'batches' in data and data['batches']:
                batches = data['batches']
                total_guests = sum(len(batch.get('guests', [])) for batch in batches)
                
                info_lines = []
                info_lines.append('📋 已保存的参观活动:')
                
                for i, batch in enumerate(batches):
                    activity = batch.get('activity', {})
                    guests = batch.get('guests', [])
                    date_info = activity.get('date', '未知日期')
                    event_info = activity.get('event', '未知事项')
                    info_lines.append(f'{i+1}. {date_info} - {event_info} ({len(guests)}位来宾)')
                
                info_lines.append(f'\n📊 共{len(batches)}个活动, 累计{total_guests}位来宾')
                
                self.saved_data_label.text = '\n'.join(info_lines)
                self.saved_data_label.color = (0.2, 0.5, 0.2, 1)
                
                # 动态调整高度
                self.saved_data_label.text_size = (self.saved_data_label.width, None)
                self.saved_data_label.height = max(100, len(info_lines) * 25)
            else:
                self.saved_data_label.text = '暂无保存的数据'
                self.saved_data_label.color = (0.6, 0.6, 0.6, 1)
                self.saved_data_label.height = 100
        except Exception as e:
            print(f'刷新数据显示错误: {e}')
            self.saved_data_label.text = '数据加载出错'
            self.saved_data_label.color = (0.8, 0.2, 0.2, 1)
    
    def show_message(self, title, message):
        """显示消息对话框"""
        content = BoxLayout(orientation='vertical', spacing=10)
        
        label = Label(text=message, text_size=(300, None), halign='center')
        content.add_widget(label)
        
        button = Button(text='确定', size_hint_y=None, height='50dp')
        button.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.6)
        )
        popup.open()