#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AgentDoc 模型管理工具

提供模型下载、测试、管理的统一命令行界面。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 避免与标准库queue模块冲突
if str(project_root) in sys.path:
    # 临时移除可能冲突的路径
    temp_paths = [p for p in sys.path if 'queue' not in p]
    sys.path = temp_paths + [str(project_root)]

try:
    from models.downloader import ModelDownloader
    from models.test_models import ModelTester
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装必要的依赖包")
    sys.exit(1)


def print_banner():
    """打印横幅"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    AgentDoc 模型管理工具                      ║
║                                                              ║
║  支持 Qwen2.5 系列模型的下载、测试和管理                        ║
╚══════════════════════════════════════════════════════════════╝
""")


def cmd_list_models(args):
    """列出所有支持的模型"""
    downloader = ModelDownloader()
    
    print("\n📋 支持的模型列表:")
    print("=" * 80)
    
    for name, info in downloader.list_models().items():
        status = "✅ 已下载" if downloader.is_model_downloaded(name) else "⬜ 未下载"
        print(f"\n🤖 {name}")
        print(f"   大小: {info.size}")
        print(f"   状态: {status}")
        print(f"   描述: {info.description}")
        if downloader.is_model_downloaded(name):
            path = downloader.get_model_path(name)
            print(f"   路径: {path}")


def cmd_download_model(args):
    """下载模型"""
    if not args.model:
        print("❌ 错误: 请指定模型名称 --model")
        return
    
    downloader = ModelDownloader()
    
    print(f"\n📥 开始下载模型: {args.model}")
    
    # 显示模型信息
    model_info = downloader.get_model_info(args.model)
    if model_info:
        print(f"📊 模型大小: {model_info.size}")
        print(f"📝 描述: {model_info.description}")
        print(f"🔗 仓库: {model_info.repo_id}")
        
        if args.modelscope:
            print("🌐 使用 ModelScope 镜像加速")
        
        print("\n⏳ 下载中，请耐心等待...")
    
    success = downloader.download_model(
        args.model,
        force=args.force,
        use_modelscope=args.modelscope
    )
    
    if success:
        print(f"\n✅ 模型 {args.model} 下载成功!")
        path = downloader.get_model_path(args.model)
        print(f"📁 保存路径: {path}")
    else:
        print(f"\n❌ 模型 {args.model} 下载失败")


def cmd_test_model(args):
    """测试模型"""
    if not args.model:
        print("❌ 错误: 请指定模型名称 --model")
        return
    
    tester = ModelTester()
    
    print(f"\n🧪 开始测试模型: {args.model}")
    
    if args.quick:
        # 快速测试
        prompt = args.prompt or "你好，请介绍一下你自己。"
        result = tester.test_model_inference(args.model, prompt)
        
        print("\n📋 快速测试结果:")
        print("-" * 50)
        print(f"💬 提示词: {result['prompt']}")
        print(f"✅ 成功: {result['inference_success']}")
        
        if result['inference_success']:
            print(f"⏱️  推理时间: {result['inference_time']:.2f}s")
            print(f"💭 模型回复:\n{result['response']}")
        else:
            print(f"❌ 错误: {result['error']}")
    else:
        # 完整测试
        result = tester.run_full_test(args.model)
        
        print("\n📋 完整测试结果:")
        print("-" * 50)
        
        # 加载测试结果
        load_result = result['load_result']
        print(f"🔄 模型加载: {'✅ 成功' if load_result['load_success'] else '❌ 失败'}")
        
        if load_result['load_success']:
            print(f"⏱️  加载时间: {load_result['load_time']:.2f}s")
            model_info = load_result['model_info']
            print(f"📊 模型参数: {model_info['num_parameters']:,}")
            print(f"🖥️  运行设备: {model_info['device']}")
            
            # 推理测试结果
            print("\n💭 推理测试:")
            for i, inf_result in enumerate(result['inference_results'], 1):
                status = "✅" if inf_result['inference_success'] else "❌"
                print(f"  {i}. {status} {inf_result['prompt'][:30]}...")
                if inf_result['inference_success']:
                    print(f"     ⏱️ {inf_result['inference_time']:.2f}s")
                    print(f"     💬 {inf_result['response'][:60]}...")
        else:
            print(f"❌ 加载错误: {load_result['error']}")


def cmd_remove_model(args):
    """删除模型"""
    if not args.model:
        print("❌ 错误: 请指定模型名称 --model")
        return
    
    downloader = ModelDownloader()
    
    if not downloader.is_model_downloaded(args.model):
        print(f"⚠️  模型 {args.model} 未下载")
        return
    
    # 确认删除
    if not args.force:
        response = input(f"\n⚠️  确定要删除模型 {args.model} 吗? (y/N): ")
        if response.lower() != 'y':
            print("❌ 取消删除")
            return
    
    success = downloader.remove_model(args.model)
    if success:
        print(f"\n✅ 模型 {args.model} 删除成功")
    else:
        print(f"\n❌ 模型 {args.model} 删除失败")


def cmd_status(args):
    """显示状态"""
    downloader = ModelDownloader()
    
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
        description="AgentDoc 模型管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s list                          # 列出所有模型
  %(prog)s download -m qwen2.5-7b-instruct  # 下载模型
  %(prog)s test -m qwen2.5-7b-instruct      # 测试模型
  %(prog)s test -m qwen2.5-7b-instruct --quick  # 快速测试
  %(prog)s status                        # 查看状态
  %(prog)s remove -m qwen2.5-7b-instruct    # 删除模型
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有支持的模型')
    
    # download 命令
    download_parser = subparsers.add_parser('download', help='下载模型')
    download_parser.add_argument('--model', '-m', required=True, help='模型名称')
    download_parser.add_argument('--force', '-f', action='store_true', help='强制重新下载')
    download_parser.add_argument('--modelscope', action='store_true', help='使用ModelScope镜像')
    
    # test 命令
    test_parser = subparsers.add_parser('test', help='测试模型')
    test_parser.add_argument('--model', '-m', required=True, help='模型名称')
    test_parser.add_argument('--quick', '-q', action='store_true', help='快速测试')
    test_parser.add_argument('--prompt', '-p', help='自定义测试提示词')
    
    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='删除模型')
    remove_parser.add_argument('--model', '-m', required=True, help='模型名称')
    remove_parser.add_argument('--force', '-f', action='store_true', help='强制删除，不询问')
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='显示模型状态')
    
    args = parser.parse_args()
    
    # 显示横幅
    print_banner()
    
    # 执行命令
    if args.command == 'list':
        cmd_list_models(args)
    elif args.command == 'download':
        cmd_download_model(args)
    elif args.command == 'test':
        cmd_test_model(args)
    elif args.command == 'remove':
        cmd_remove_model(args)
    elif args.command == 'status':
        cmd_status(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()