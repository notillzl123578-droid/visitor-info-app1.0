"""主界面 - 文件上传"""
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, ObjectProperty
from kivy.graphics import Color, RoundedRectangle
from app.services import WordParser, TextExtractor, DocParser, OCRService
from app.models import ExtractedData, Database


class MainScreen(Screen):
    """主界面"""
    files = ListProperty([])
    extracted_data = ObjectProperty(ExtractedData())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word_parser = WordParser()
        self.text_extractor = TextExtractor()
        self.doc_parser = DocParser()
        self.ocr_service = OCRService()
        self.database = Database()
        self.build_ui()
        
        # 加载上次未导出的数据
        self.load_previous_session()
    
    def build_ui(self):
        """构建UI"""
        # 设置背景色（蓝白渐变效果）
        with self.canvas.before:
            Color(0.95, 0.97, 1, 1)  # 淡蓝白色背景
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题区域
        title_box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)
        
        title = Label(
            text='来宾信息提取工具',
            size_hint_y=None,
            height=50,
            font_size='28sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            bold=True,
            color=(0.2, 0.4, 0.8, 1)  # 深蓝色
        )
        title_box.add_widget(title)
        
        subtitle = Label(
            text='支持Word、Excel、图片、文本混合分析',
            size_hint_y=None,
            height=30,
            font_size='14sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.5, 0.5, 0.5, 1)  # 灰色
        )
        title_box.add_widget(subtitle)
        
        layout.add_widget(title_box)
        
        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)
        
        choose_file_btn = self._create_button('📁 选择文件', (0.3, 0.6, 1, 1))
        choose_file_btn.bind(on_press=self.choose_file)
        btn_layout.add_widget(choose_file_btn)
        
        clear_btn = self._create_button('🗑️ 清空', (0.9, 0.4, 0.4, 1))
        clear_btn.bind(on_press=self.clear_files)
        btn_layout.add_widget(clear_btn)
        
        history_btn = self._create_button('📜 历史', (0.5, 0.7, 0.9, 1))
        history_btn.bind(on_press=self.show_history)
        btn_layout.add_widget(history_btn)
        
        layout.add_widget(btn_layout)
        
        # 文件列表区域
        file_box = BoxLayout(orientation='vertical', spacing=10)
        
        file_label = Label(
            text='已选文件:',
            size_hint_y=None,
            height=30,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        file_label.bind(size=file_label.setter('text_size'))
        file_box.add_widget(file_label)
        
        scroll = ScrollView(size_hint=(1, 0.4))
        self.file_list_label = Label(
            text='未选择文件',
            font_size='14sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.6, 0.6, 0.6, 1),
            halign='left',
            valign='top'
        )
        self.file_list_label.bind(size=self.file_list_label.setter('text_size'))
        scroll.add_widget(self.file_list_label)
        file_box.add_widget(scroll)
        
        layout.add_widget(file_box)
        
        # 已保存数据显示区域
        saved_data_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.5)  # 增加高度
        
        # 标题行（包含导出按钮）
        saved_title_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        
        saved_label = Label(
            text='已保存的数据:',
            size_hint_x=0.6,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            bold=True
        )
        saved_label.bind(size=saved_label.setter('text_size'))
        saved_title_row.add_widget(saved_label)
        
        # 导出Excel按钮
        export_saved_btn = self._create_button('📥 导出Excel', (0.2, 0.7, 0.3, 1), height=40)
        export_saved_btn.bind(on_press=self.export_saved_data)
        saved_title_row.add_widget(export_saved_btn)
        
        saved_data_box.add_widget(saved_title_row)
        
        self.saved_data_label = Label(
            text='暂无保存的数据',
            font_size='14sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.6, 0.6, 0.6, 1),
            halign='left',
            valign='top'
        )
        self.saved_data_label.bind(size=self.saved_data_label.setter('text_size'))
        saved_data_box.add_widget(self.saved_data_label)
        
        layout.add_widget(saved_data_box)
        
        # 文本输入区域
        text_box = BoxLayout(orientation='vertical', spacing=10, size_hint_y=0.6)
        
        text_label = Label(
            text='或直接输入/粘贴文字:',
            size_hint_y=None,
            height=30,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.3, 0.3, 0.3, 1),
            halign='left'
        )
        text_label.bind(size=text_label.setter('text_size'))
        text_box.add_widget(text_label)
        
        self.text_input = TextInput(
            multiline=True,
            hint_text='在这里输入或粘贴文字内容...\n例如：\n6月10日参观活动\n陪同领导：张三\n陪同部门：办公室',
            font_size='14sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(1, 1, 1, 1),
            foreground_color=(0.2, 0.2, 0.2, 1)
        )
        text_box.add_widget(self.text_input)
        
        layout.add_widget(text_box)
        
        # 处理按钮
        process_btn = self._create_button('▶️ 开始处理', (0.2, 0.7, 0.3, 1), height=70)
        process_btn.bind(on_press=self.process_files)
        layout.add_widget(process_btn)
        
        self.add_widget(layout)
    
    def _create_button(self, text, color, height=60):
        """创建圆角按钮"""
        btn = Button(
            text=text,
            size_hint_y=None,
            height=height,
            font_size='16sp',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_normal='',
            background_color=color,
            bold=True
        )
        
        # 添加圆角效果
        with btn.canvas.before:
            Color(*color)
            btn.bg_rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[15])
        
        def update_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        btn.bind(pos=update_bg, size=update_bg)
        
        return btn
    
    def _update_bg(self, instance, value):
        """更新背景"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def load_previous_session(self):
        """加载上次未导出的数据"""
        self.refresh_saved_data()
    
    def refresh_saved_data(self):
        """刷新已保存数据的显示 - 简化版本"""
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
                
                info_lines.append(f'\\n📊 共{len(batches)}个活动, 累计{total_guests}位来宾')
                
                self.saved_data_label.text = '\\n'.join(info_lines)
                self.saved_data_label.color = (0.2, 0.5, 0.2, 1)
                print(f'✓ 已加载保存数据: 累计{total_guests}位来宾')
            else:
                self.saved_data_label.text = '暂无保存的数据'
                self.saved_data_label.color = (0.6, 0.6, 0.6, 1)
        except Exception as e:
            print(f'刷新数据显示错误: {e}')
            self.saved_data_label.text = '数据加载出错'
            self.saved_data_label.color = (0.8, 0.2, 0.2, 1)
    
    def choose_file(self, instance):
        """选择文件"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        file_chooser = FileChooserListView(
            filters=['*.docx', '*.doc', '*.txt', '*.jpg', '*.jpeg', '*.png', '*.bmp', '*.csv', '*.xlsx']
        )
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        select_btn = Button(
            text='选择',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.3, 0.6, 1, 1)
        )
        cancel_btn = Button(
            text='取消',
            font_name='C:/Windows/Fonts/msyh.ttc',
            background_color=(0.7, 0.7, 0.7, 1)
        )
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='选择文件',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(btn):
            if file_chooser.selection:
                self.files.extend(file_chooser.selection)
                self.update_file_list()
            popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def update_file_list(self):
        """更新文件列表显示"""
        if not self.files:
            self.file_list_label.text = '未选择文件'
            self.file_list_label.color = (0.6, 0.6, 0.6, 1)
        else:
            file_names = []
            for f in self.files:
                name = f.split('/')[-1].split('\\')[-1]
                ext = name.split('.')[-1].lower()
                
                # 添加文件类型图标
                if ext in ['docx', 'doc']:
                    icon = '📄'
                elif ext in ['jpg', 'jpeg', 'png', 'bmp']:
                    icon = '🖼️'
                elif ext == 'txt':
                    icon = '📝'
                elif ext in ['csv', 'xlsx']:
                    icon = '📊'
                else:
                    icon = '📎'
                
                file_names.append(f'{icon} {name}')
            
            self.file_list_label.text = '\n'.join(file_names)
            self.file_list_label.color = (0.2, 0.2, 0.2, 1)
    
    def clear_files(self, instance):
        """清空文件"""
        self.files = []
        self.update_file_list()
    
    def show_history(self, instance):
        """显示历史记录"""
        self.manager.current = 'history'
    
    def export_saved_data(self, instance):
        """导出已保存的数据 - 简化版本"""
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
            
            # 添加到导出历史
            filename = os.path.basename(file_path)
            self.database.add_export_history(filename, file_path, total_guests, data['batches'])
            
            # 清空数据
            self.database.clear_current_session()
            self.refresh_saved_data()
            
            message = f'导出成功！\\n文件: {filename}\\n共{total_guests}条数据\\n\\n数据已清空，可开始新的录入'
            self.show_message('导出成功', message)
            
        except Exception as e:
            error_msg = f'导出失败: {str(e)}'
            print(f'导出错误: {error_msg}')
            self.show_message('导出失败', error_msg)

    def process_files(self, instance):
        """处理文件"""
        # 检查是否有文件或文本输入
        has_files = len(self.files) > 0
        has_text = self.text_input.text.strip() != ''
        
        if not has_files and not has_text:
            self.show_message('提示', '请选择文件或输入文字')
            return
        
        # 重置extracted_data，准备新的处理
        self.extracted_data = ExtractedData()
        
        # 处理文本输入
        if has_text:
            text = self.text_input.text
            self._process_extracted_data(text, [])
            print('✓ 已处理文本输入')
        
        # 处理文件
        if has_files:
            for file_path in self.files:
                self.process_single_file(file_path)
        
        # 自动保存到数据库
        activity_dict = {
            'date': self.extracted_data.activity.date,
            'event': self.extracted_data.activity.event,
            'leader': self.extracted_data.activity.leader,
            'department': self.extracted_data.activity.department,
            'route': self.extracted_data.activity.route
        }
        guests_list = [
            {
                'company': g.company,
                'name': g.name,
                'position': g.position
            }
            for g in self.extracted_data.guests
        ]
        self.database.save_current_session(activity_dict, guests_list)
        
        # 显示结果
        guest_count = len(self.extracted_data.guests)
        
        if has_text and has_files:
            message = f'提取完成！\n文本+文件已处理\n来宾: {guest_count}位\n数据已自动保存'
        elif has_text:
            message = f'提取完成！\n文本已处理\n来宾: {guest_count}位\n数据已自动保存'
        else:
            message = f'提取完成！\n来宾: {guest_count}位\n数据已自动保存'
        
        # 清空文件列表和文本输入
        self.files = []
        self.text_input.text = ''
        self.update_file_list()
        
        self.show_message('提取成功', message, self.go_to_preview)
    
    def process_single_file(self, file_path: str):
        """处理单个文件"""
        print(f'处理文件: {file_path}')
        
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'docx':
            # 解析.docx文档
            text, guests = self.word_parser.parse_docx(file_path)
            self._process_extracted_data(text, guests)
        
        elif ext == 'doc':
            # 解析.doc文档
            text, guests = self.doc_parser.parse_doc(file_path)
            self._process_extracted_data(text, guests)
        
        elif ext == 'txt':
            # 读取文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self._process_extracted_data(text, [])
        
        elif ext in ['csv', 'xlsx']:
            # 读取Excel文件
            self._process_excel_file(file_path)
        
        elif ext in ['jpg', 'jpeg', 'png', 'bmp']:
            # OCR识别图片
            if self.ocr_service.is_available():
                text = self.ocr_service.extract_text(file_path)
                self._process_extracted_data(text, [])
            else:
                print('OCR服务不可用，跳过图片文件')
    
    def _process_extracted_data(self, text: str, guests: list):
        """处理提取的数据"""
        # 提取活动信息（累积模式）
        self.extracted_data.activity = self.text_extractor.extract_activity_info(
            text, self.extracted_data.activity
        )
        
        # 累积来宾信息（从Word表格）
        for guest in guests:
            if not any(g.name == guest.name and g.company == guest.company 
                      for g in self.extracted_data.guests):
                self.extracted_data.guests.append(guest)
        
        # 从文本中提取来宾信息（新增）
        text_guests = self.text_extractor.extract_guests_from_text(text)
        for guest in text_guests:
            if not any(g.name == guest.name and g.company == guest.company 
                      for g in self.extracted_data.guests):
                self.extracted_data.guests.append(guest)
    
    def _process_excel_file(self, file_path: str):
        """处理Excel文件"""
        print(f'读取Excel文件: {file_path}')
        
        try:
            import csv
            
            # 读取CSV文件
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # 提取来宾信息
                    if row.get('姓名'):
                        from app.models import GuestInfo
                        guest = GuestInfo(
                            company=row.get('来宾单位', ''),
                            name=row.get('姓名', ''),
                            position=row.get('职务', '')
                        )
                        
                        # 避免重复
                        if not any(g.name == guest.name and g.company == guest.company 
                                  for g in self.extracted_data.guests):
                            self.extracted_data.guests.append(guest)
                    
                    # 提取活动信息（只取第一行）
                    if not self.extracted_data.activity.date and row.get('日期'):
                        self.extracted_data.activity.date = row.get('日期', '')
                        self.extracted_data.activity.event = row.get('参观事项', '')
                        self.extracted_data.activity.leader = row.get('陪同领导', '')
                        self.extracted_data.activity.department = row.get('陪同部门', '')
                        self.extracted_data.activity.route = row.get('参观路线', '')
            
            print(f'✓ 已从Excel加载 {len(self.extracted_data.guests)} 位来宾')
            
        except Exception as e:
            print(f'读取Excel文件失败: {e}')
            self.show_message('错误', f'读取Excel文件失败: {e}')
    
    def go_to_preview(self):
        """跳转到预览页面"""
        preview_screen = self.manager.get_screen('preview')
        preview_screen.load_data(self.extracted_data)
        self.manager.current = 'preview'
    
    def show_message(self, title: str, message: str, callback=None):
        """显示消息"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            font_name='C:/Windows/Fonts/msyh.ttc',
            color=(0.2, 0.2, 0.2, 1)
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
            size_hint=(0.8, 0.4)
        )
        
        def on_close(instance):
            popup.dismiss()
            if callback:
                callback()
        
        btn.bind(on_press=on_close)
        popup.open()
