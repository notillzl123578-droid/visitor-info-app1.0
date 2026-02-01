"""OCR图片识别服务"""
import os
from typing import Optional


class OCRService:
    """OCR图片识别服务"""
    
    def __init__(self, tesseract_path: str = None):
        """
        初始化OCR服务
        
        Args:
            tesseract_path: Tesseract可执行文件路径
        """
        self.tesseract_available = False
        
        try:
            import pytesseract
            from PIL import Image, ImageEnhance, ImageFilter
            
            self.Image = Image
            self.ImageEnhance = ImageEnhance
            self.ImageFilter = ImageFilter
            
            # 设置Tesseract路径
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
            elif os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            self.pytesseract = pytesseract
            self.tesseract_available = True
            print('✓ OCR服务已启用')
            
        except ImportError:
            print('警告: pytesseract或Pillow未安装，OCR功能不可用')
            print('请运行: pip install pytesseract Pillow')
            print('并下载Tesseract: https://github.com/UB-Mannheim/tesseract/wiki')
    
    def extract_text(self, image_path: str, lang='chi_sim+eng') -> str:
        """
        从图片中提取文本
        
        Args:
            image_path: 图片文件路径
            lang: 识别语言（chi_sim=简体中文, eng=英文）
            
        Returns:
            提取的文本内容
        """
        if not self.tesseract_available:
            return ''
        
        try:
            # 打开图片
            image = self.Image.open(image_path)
            
            # 预处理图片
            processed_image = self._preprocess_image(image)
            
            # OCR识别
            text = self.pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config='--psm 6'  # 假设统一的文本块
            )
            
            return text.strip()
            
        except Exception as e:
            print(f'OCR识别失败: {e}')
            return ''
    
    def _preprocess_image(self, image):
        """
        预处理图片以提高OCR准确率
        
        Args:
            image: PIL图片对象
            
        Returns:
            处理后的图片
        """
        # 转换为灰度图
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增强对比度
        enhancer = self.ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # 锐化
        image = image.filter(self.ImageFilter.SHARPEN)
        
        # 调整大小（如果太小）
        width, height = image.size
        if width < 1000:
            scale = 1000 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, self.Image.Resampling.LANCZOS)
        
        return image
    
    def is_available(self) -> bool:
        """检查OCR服务是否可用"""
        return self.tesseract_available
    
    def get_available_languages(self) -> list:
        """获取可用的语言包"""
        if not self.tesseract_available:
            return []
        
        try:
            langs = self.pytesseract.get_languages()
            return langs
        except:
            return []
