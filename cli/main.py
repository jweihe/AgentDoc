"""命令行主入口"""

import asyncio
import click
from pathlib import Path
from ..core.config import get_settings
from ..models.manager import ModelManager
from ..processors.pdf_processor import PDFProcessor
from ..core.logger import get_logger

logger = get_logger(__name__)

@click.command()
@click.option('--pdf', required=True, help='PDF文件路径')
@click.option('--model', default='qwen2.5-vl', help='使用的模型')
@click.option('--output-dir', default='output', help='输出目录')
@click.option('--cpu-only', is_flag=True, help='仅使用CPU')
@click.option('--include-pages', is_flag=True, help='包含页码')
def main(pdf, model, output_dir, cpu_only, include_pages):
    """DocuMind命令行工具"""
    asyncio.run(process_pdf(pdf, model, output_dir, cpu_only, include_pages))

async def process_pdf(pdf_path, model_name, output_dir, cpu_only, include_pages):
    """处理PDF文件"""
    try:
        settings = get_settings()
        settings.model.cpu_only = cpu_only
        settings.processing.include_page_numbers = include_pages
        
        manager = ModelManager()
        model = manager.load_model(model_name)
        
        processor = PDFProcessor(model, settings)
        result = await processor.process(pdf_path, output_dir)
        
        logger.info(f"处理完成: {result}")
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise
    finally:
        manager.unload_all()

if __name__ == '__main__':
    main()