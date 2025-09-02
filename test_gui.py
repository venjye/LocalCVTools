#!/usr/bin/env python3
"""
简单的GUI测试脚本
"""
import sys

def test_pyqt5_import():
    """测试PyQt5导入"""
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        print("✅ PyQt5 导入成功")
        return True
    except ImportError as e:
        print(f"❌ PyQt5 导入失败: {e}")
        return False

def create_test_window():
    """创建测试窗口"""
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("LocalCVTools - PyQt5 测试")
    window.setGeometry(100, 100, 400, 300)
    
    # 创建中央部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout()
    
    # 添加标签
    title_label = QLabel("LocalCVTools PyQt5 测试")
    title_label.setAlignment(Qt.AlignCenter)
    font = QFont()
    font.setPointSize(16)
    font.setBold(True)
    title_label.setFont(font)
    
    status_label = QLabel("✅ PyQt5 工作正常！")
    status_label.setAlignment(Qt.AlignCenter)
    status_label.setStyleSheet("color: green; font-size: 14px;")
    
    info_label = QLabel("如果你看到这个窗口，说明PyQt5已经正确安装并可以使用。\n现在可以运行完整的LocalCVTools程序了！")
    info_label.setAlignment(Qt.AlignCenter)
    info_label.setWordWrap(True)
    
    # 添加按钮
    close_button = QPushButton("关闭测试窗口")
    close_button.clicked.connect(window.close)
    
    launch_button = QPushButton("启动 LocalCVTools")
    def launch_main():
        window.close()
        try:
            from main import main as app_main
            app_main()
        except Exception as e:
            print(f"启动主程序失败: {e}")
    
    launch_button.clicked.connect(launch_main)
    launch_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
    
    # 添加到布局
    layout.addWidget(title_label)
    layout.addWidget(status_label)
    layout.addWidget(info_label)
    layout.addStretch()
    layout.addWidget(launch_button)
    layout.addWidget(close_button)
    
    central_widget.setLayout(layout)
    
    # 显示窗口
    window.show()
    
    return app.exec_()

def main():
    """主函数"""
    print("LocalCVTools PyQt5 测试")
    print("=" * 30)
    
    # 测试导入
    if not test_pyqt5_import():
        print("\n请安装PyQt5:")
        print("pip install PyQt5")
        return 1
    
    print("\n启动测试窗口...")
    
    try:
        return create_test_window()
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
