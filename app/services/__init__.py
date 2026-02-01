from .text_extractor import TextExtractor

try:
    from .word_parser import WordParser
    from .excel_generator import ExcelGenerator
    __all__ = ['WordParser', 'TextExtractor', 'ExcelGenerator']
except ImportError:
    # Dependencies not installed yet
    __all__ = ['TextExtractor']

# Import optional services
try:
    from .doc_parser import DocParser
    __all__.append('DocParser')
except ImportError:
    pass

try:
    from .ocr_service import OCRService
    __all__.append('OCRService')
except ImportError:
    pass
