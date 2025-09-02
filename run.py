#!/usr/bin/env python3
"""
LocalCVTools 启动脚本
检查依赖并启动应用程序
"""
import sys
import os
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    required_packages = {
        'PyQt5': 'PyQt5',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }
    
    missing_packages = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """安装缺失的依赖"""
    if not packages:
        return True
    
    print(f"\n尝试安装缺失的依赖: {', '.join(packages)}")
    
    try:
        # 尝试使用pip安装
        cmd = [sys.executable, '-m', 'pip', 'install'] + packages
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装成功")
            return True
        else:
            print(f"❌ pip安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def main():
    """主函数"""
    print("LocalCVTools 启动检查")
    print("=" * 40)
    
    # 检查依赖
    missing = check_dependencies()
    
    if missing:
        print(f"\n发现 {len(missing)} 个缺失的依赖包")
        
        # 询问是否自动安装
        try:
            response = input("\n是否尝试自动安装? (y/n): ").lower().strip()
            if response in ['y', 'yes', '是']:
                if install_dependencies(missing):
                    print("\n重新检查依赖...")
                    missing = check_dependencies()
                else:
                    print("\n自动安装失败，请手动安装依赖:")
                    print("pip install PyQt5 opencv-python numpy Pillow")
                    return 1
            else:
                print("\n请手动安装依赖后再运行:")
                print("pip install PyQt5 opencv-python numpy Pillow")
                return 1
        except KeyboardInterrupt:
            print("\n\n用户取消")
            return 1
    
    if missing:
        print("\n仍有依赖缺失，无法启动应用程序")
        return 1
    
    print("\n" + "=" * 40)
    print("🚀 启动 LocalCVTools...")
    
    try:
        # 启动主程序
        from main import main as app_main
        return app_main()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
