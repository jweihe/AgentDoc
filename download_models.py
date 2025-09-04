#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AgentDoc 模型下载脚本

简单的模型下载工具，支持 Qwen2.5 系列模型。
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from huggingface_hub import snapshot_download, hf_hub_download
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:
    print("正在安装 huggingface_hub...")
    os.system("pip install huggingface_hub")
    from huggingface_hub import snapshot_download, hf_hub_download
    from huggingface_hub.utils import HfHubHTTPError


class SimpleModelDownloader:
    """简单的模型下载器"""
    
    def __init__(self, download_dir: str = None):
        """初始化下载器
        
        Args:
            download_dir: 下载目录，默认为 models/downloads
        """
        if download_dir is None:
            self.download_dir = Path(__file__).parent / "models" / "downloads"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 支持的模型配置
        self.models = {
            # Qwen2.5 系列
            "qwen2.5-0.5b-instruct": {
                "repo_id": "Qwen/Qwen2.5-0.5B-Instruct",
                "size": "~1GB",
                "description": "Qwen2.5 0.5B 指令微调模型，轻量级版本"
            },
            "qwen2.5-1.5b-instruct": {
                "repo_id": "Qwen/Qwen2.5-1.5B-Instruct",
                "size": "~3GB",
                "description": "Qwen2.5 1.5B 指令微调模型，平衡性能与资源"
            },
            "qwen2.5-3b-instruct": {
                "repo_id": "Qwen/Qwen2.5-3B-Instruct",
                "size": "~6GB",
                "description": "Qwen2.5 3B 指令微调模型，中等规模"
            },
            "qwen2.5-7b-instruct": {
                "repo_id": "Qwen/Qwen2.5-7B-Instruct",
                "size": "~15GB",
                "description": "Qwen2.5 7B 指令微调模型，高性能版本"
            },
            "qwen2.5-14b-instruct": {
                "repo_id": "Qwen/Qwen2.5-14B-Instruct",
                "size": "~30GB",
                "description": "Qwen2.5 14B 指令微调模型，大规模版本"
            },
            "qwen2.5-32b-instruct": {
                "repo_id": "Qwen/Qwen2.5-32B-Instruct",
                "size": "~65GB",
                "description": "Qwen2.5 32B 指令微调模型，超大规模版本"
            },
            "qwen2.5-72b-instruct": {
                "repo_id": "Qwen/Qwen2.5-72B-Instruct",
                "size": "~145GB",
                "description": "Qwen2.5 72B 指令微调模型，旗舰版本"
            },
            # Qwen3 系列
            "qwen3-0.6b": {
                "repo_id": "Qwen/Qwen3-0.6B",
                "size": "~1.2GB",
                "description": "Qwen3 0.6B 基础模型，新一代超轻量级版本"
            },
            "qwen3-1.7b": {
                "repo_id": "Qwen/Qwen3-1.7B",
                "size": "~3.5GB",
                "description": "Qwen3 1.7B 基础模型，新一代轻量级版本"
            },
            "qwen3-4b": {
                "repo_id": "Qwen/Qwen3-4B",
                "size": "~8GB",
                "description": "Qwen3 4B 基础模型，新一代中等规模版本"
            },
            "qwen3-8b": {
                "repo_id": "Qwen/Qwen3-8B",
                "size": "~16GB",
                "description": "Qwen3 8B 基础模型，新一代高性能版本"
            },
            "qwen3-14b": {
                "repo_id": "Qwen/Qwen3-14B",
                "size": "~28GB",
                "description": "Qwen3 14B 基础模型，新一代大规模版本"
            },
            "qwen3-32b": {
                "repo_id": "Qwen/Qwen3-32B",
                "size": "~64GB",
                "description": "Qwen3 32B 基础模型，新一代超大规模版本"
            }
        }
    
    def list_models(self) -> Dict[str, Dict]:
        """列出所有支持的模型"""
        return self.models
    
    def is_model_downloaded(self, model_name: str) -> bool:
        """检查模型是否已下载"""
        if model_name not in self.models:
            return False
        
        model_path = self.download_dir / model_name
        return model_path.exists() and any(model_path.iterdir())
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """获取模型路径"""
        if not self.is_model_downloaded(model_name):
            return None
        return self.download_dir / model_name
    
    def download_model(self, model_name: str, force: bool = False, use_modelscope: bool = False) -> bool:
        """下载模型
        
        Args:
            model_name: 模型名称
            force: 是否强制重新下载
            use_modelscope: 是否使用ModelScope镜像
        
        Returns:
            bool: 下载是否成功
        """
        if model_name not in self.models:
            print(f"❌ 不支持的模型: {model_name}")
            print(f"支持的模型: {', '.join(self.models.keys())}")
            return False
        
        model_info = self.models[model_name]
        repo_id = model_info["repo_id"]
        local_dir = self.download_dir / model_name
        
        # 检查是否已下载
        if self.is_model_downloaded(model_name) and not force:
            print(f"✅ 模型 {model_name} 已存在，使用 --force 强制重新下载")
            return True
        
        print(f"📥 开始下载模型: {model_name}")
        print(f"📊 预估大小: {model_info['size']}")
        print(f"🔗 仓库: {repo_id}")
        
        if use_modelscope:
            print("🌐 使用 ModelScope 镜像加速")
            # ModelScope 镜像配置
            os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        try:
            # 创建本地目录
            local_dir.mkdir(parents=True, exist_ok=True)
            
            print("⏳ 下载中，请耐心等待...")
            start_time = time.time()
            
            # 下载模型
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(local_dir),
                resume_download=True,
                local_dir_use_symlinks=False
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ 模型 {model_name} 下载成功!")
            print(f"⏱️  下载耗时: {duration:.1f}秒")
            print(f"📁 保存路径: {local_dir}")
            
            # 保存下载信息
            info_file = local_dir / "download_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "model_name": model_name,
                    "repo_id": repo_id,
                    "download_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_seconds": duration,
                    "size": model_info['size']
                }, f, indent=2, ensure_ascii=False)
            
            return True
            
        except HfHubHTTPError as e:
            print(f"❌ 下载失败 (HTTP错误): {e}")
            return False
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """删除模型"""
        if not self.is_model_downloaded(model_name):
            print(f"⚠️  模型 {model_name} 未下载")
            return False
        
        model_path = self.get_model_path(model_name)
        try:
            import shutil
            shutil.rmtree(model_path)
            print(f"✅ 模型 {model_name} 删除成功")
            return True
        except Exception as e:
            print(f"❌ 删除失败: {e}")
            return False
    
    def get_downloaded_models(self) -> List[str]:
        """获取已下载的模型列表"""
        downloaded = []
        for model_name in self.models.keys():
            if self.is_model_downloaded(model_name):
                downloaded.append(model_name)
        return downloaded


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    AgentDoc 模型下载工具                      ║
║                                                              ║
║  支持 Qwen2.5 系列模型的下载和管理                            ║
╚══════════════════════════════════════════════════════════════╝
""")


def cmd_list(downloader):
    """列出所有模型"""
    print("\n📋 支持的模型列表:")
    print("=" * 80)
    
    for name, info in downloader.list_models().items():
        status = "✅ 已下载" if downloader.is_model_downloaded(name) else "⬜ 未下载"
        print(f"\n🤖 {name}")
        print(f"   大小: {info['size']}")
        print(f"   状态: {status}")
        print(f"   描述: {info['description']}")
        if downloader.is_model_downloaded(name):
            path = downloader.get_model_path(name)
            print(f"   路径: {path}")


def cmd_download(downloader, model_name, force=False, use_modelscope=False):
    """下载模型"""
    success = downloader.download_model(model_name, force=force, use_modelscope=use_modelscope)
    return success


def cmd_status(downloader):
    """显示状态"""
    print("\n📊 AgentDoc 模型状态")
    print("=" * 50)
    
    # 下载目录信息
    print(f"📁 下载目录: {downloader.download_dir}")
    
    # 已下载模型
    downloaded = downloader.get_downloaded_models()
    print(f"\n📦 已下载模型 ({len(downloaded)} 个):")
    
    if downloaded:
        total_size = 0
        for model in downloaded:
            path = downloader.get_model_path(model)
            try:
                # 计算目录大小
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_gb = size / (1024**3)
                total_size += size_gb
                print(f"  ✅ {model} ({size_gb:.1f} GB)")
            except:
                print(f"  ✅ {model} (大小未知)")
        
        print(f"\n💾 总占用空间: {total_size:.1f} GB")
    else:
        print("  (暂无)")
    
    # 可用模型
    all_models = downloader.list_models()
    available = len(all_models) - len(downloaded)
    print(f"\n🔄 可下载模型: {available} 个")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AgentDoc 模型下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python3 download_models.py list                          # 列出所有模型
  python3 download_models.py download qwen2.5-7b-instruct  # 下载模型
  python3 download_models.py download qwen2.5-7b-instruct --force  # 强制重新下载
  python3 download_models.py download qwen2.5-7b-instruct --modelscope  # 使用镜像
  python3 download_models.py status                        # 查看状态
  python3 download_models.py remove qwen2.5-7b-instruct    # 删除模型
"""
    )
    
    parser.add_argument('command', choices=['list', 'download', 'status', 'remove'], help='命令')
    parser.add_argument('model', nargs='?', help='模型名称')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新下载')
    parser.add_argument('--modelscope', action='store_true', help='使用ModelScope镜像')
    
    args = parser.parse_args()
    
    # 显示横幅
    print_banner()
    
    # 创建下载器
    downloader = SimpleModelDownloader()
    
    # 执行命令
    if args.command == 'list':
        cmd_list(downloader)
    elif args.command == 'download':
        if not args.model:
            print("❌ 错误: 请指定模型名称")
            parser.print_help()
            return
        cmd_download(downloader, args.model, args.force, args.modelscope)
    elif args.command == 'status':
        cmd_status(downloader)
    elif args.command == 'remove':
        if not args.model:
            print("❌ 错误: 请指定模型名称")
            parser.print_help()
            return
        
        # 确认删除
        if not args.force:
            response = input(f"\n⚠️  确定要删除模型 {args.model} 吗? (y/N): ")
            if response.lower() != 'y':
                print("❌ 取消删除")
                return
        
        downloader.remove_model(args.model)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()