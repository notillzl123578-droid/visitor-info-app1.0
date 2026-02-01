"""移动版应用入口 - 简化版本"""
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.text import LabelBase
from kivy.utils import platform
from app.ui.mobile_main_screen import MobileMainScreen


class VisitorInfoMobileApp(App):
    """来宾信息提取应用 - 移动版"""
    
    def build(self):
        """构建应用"""
        # 注册中文字体（移动版）
        self.register_mobile_fonts()
        
        sm = ScreenManager()
        
        # 添加移动版主界面
        main_screen = MobileMainScreen(name='main')
        sm.add_widget(main_screen)
        
        return sm
    
    def register_mobile_fonts(self):
        """注册移动设备中文字体"""
        if platform == 'android':
            # Android系统字体路径
            font_paths = [
                '/system/fonts/NotoSansCJK-Regular.ttc',
                '/system/fonts/DroidSansFallback.ttf',
                '/system/fonts/NotoSansSC-Regular.otf',
            ]
        elif platform == 'ios':
            # iOS系统字体路径
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
            ]
        else:
            # 桌面版字体路径
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',
                'C:/Windows/Fonts/simhei.ttf',
            ]
        
        # 尝试注册第一个可用的字体
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(
                        name='Roboto',  # Kivy默认字体名
                        fn_regular=font_path
                    )
                    print(f'✓ 已注册中文字体: {font_path}')
                    break
                except Exception as e:
                    print(f'注册字体失败: {font_path}, 错误: {e}')
                    continue


if __name__ == '__main__':
    VisitorInfoMobileApp().run()