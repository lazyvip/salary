"""
一键逆向工具 - 自动化执行所有逆向步骤
"""
import os
import sys
import time

def print_banner():
    """打印横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           Python 软件逆向工程自动化工具                       ║
    ║           AI批量生图工具 v2.0.14 逆向分析                     ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def run_step(step_num, script_name, description):
    """
    运行逆向步骤
    
    Args:
        step_num: 步骤编号
        script_name: 脚本名称
        description: 步骤描述
    """
    print("\n" + "="*80)
    print(f"步骤 {step_num}: {description}")
    print("="*80)
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"[!] 脚本不存在: {script_path}")
        return False
    
    print(f"[*] 执行脚本: {script_name}")
    
    # 询问是否执行
    choice = input(f"\n是否执行此步骤? (y/n/s=跳过所有确认): ").strip().lower()
    
    if choice == 's':
        return 'skip_all'
    elif choice != 'y':
        print("[*] 跳过此步骤")
        return True
    
    # 执行脚本
    try:
        exec(open(script_path, encoding='utf-8').read(), {'__name__': '__main__'})
        print(f"\n[+] 步骤 {step_num} 完成！")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"\n[!] 步骤 {step_num} 执行失败: {e}")
        print(f"[!] 错误详情: {type(e).__name__}")
        
        choice = input("\n是否继续下一步? (y/n): ").strip().lower()
        return choice == 'y'

def manual_mode():
    """手动模式 - 逐步执行"""
    print_banner()
    print("\n[*] 手动模式 - 逐步执行每个步骤")
    print("[*] 你可以选择执行或跳过每个步骤\n")
    
    steps = [
        (1, "1_extract_pyinstaller.py", "提取 PyInstaller 打包的 exe"),
        (2, "2_decompile_pyc.py", "反编译 .pyc 字节码文件"),
        (3, "3_analyze_license.py", "分析授权机制"),
        (4, "4_crack_keygen.py", "生成注册机/破解工具"),
    ]
    
    skip_all = False
    
    for step_num, script_name, description in steps:
        if skip_all:
            print(f"\n[*] 自动执行步骤 {step_num}...")
            try:
                script_path = os.path.join(os.path.dirname(__file__), script_name)
                exec(open(script_path, encoding='utf-8').read(), {'__name__': '__main__'})
            except Exception as e:
                print(f"[!] 步骤 {step_num} 失败: {e}")
        else:
            result = run_step(step_num, script_name, description)
            if result == 'skip_all':
                skip_all = True
            elif not result:
                print("\n[!] 逆向流程中断")
                return
    
    print("\n" + "="*80)
    print("逆向分析完成！")
    print("="*80)
    print("\n接下来的步骤:")
    print("1. 查看分析报告: decompiled/license_analysis_report.txt")
    print("2. 查看授权相关代码: decompiled/license_related_code.txt")
    print("3. 根据分析结果修改 4_crack_keygen.py")
    print("4. 运行注册机生成授权码")

def quick_mode():
    """快速模式 - 自动执行所有步骤"""
    print_banner()
    print("\n[*] 快速模式 - 自动执行所有步骤")
    print("[!] 这可能需要较长时间，请耐心等待...\n")
    
    steps = [
        "1_extract_pyinstaller.py",
        "2_decompile_pyc.py",
        "3_analyze_license.py",
    ]
    
    for i, script_name in enumerate(steps, 1):
        print(f"\n{'='*80}")
        print(f"自动执行步骤 {i}/{len(steps)}: {script_name}")
        print('='*80)
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            exec(open(script_path, encoding='utf-8').read(), {'__name__': '__main__'})
            print(f"[+] 步骤 {i} 完成")
        except Exception as e:
            print(f"[!] 步骤 {i} 失败: {e}")
            if input("\n继续? (y/n): ").lower() != 'y':
                return
    
    print("\n[+] 自动化逆向分析完成！")
    print("[*] 现在可以查看分析结果并手动运行注册机")

def interactive_mode():
    """交互模式 - 只运行注册机"""
    print_banner()
    print("\n[*] 交互模式 - 直接运行注册机")
    print("[*] 假设你已经完成了前面的逆向分析步骤\n")
    
    script_path = os.path.join(os.path.dirname(__file__), "4_crack_keygen.py")
    try:
        exec(open(script_path, encoding='utf-8').read(), {'__name__': '__main__'})
    except Exception as e:
        print(f"[!] 运行失败: {e}")

def show_menu():
    """显示主菜单"""
    print_banner()
    
    print("\n请选择运行模式:\n")
    print("  1. 手动模式 - 逐步确认执行 (推荐)")
    print("  2. 快速模式 - 自动执行所有步骤")
    print("  3. 交互模式 - 只运行注册机")
    print("  4. 查看使用说明")
    print("  0. 退出")
    
    choice = input("\n请选择 (0-4): ").strip()
    
    return choice

def show_help():
    """显示使用说明"""
    help_text = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                      使用说明                                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    【逆向流程】
    
    步骤1: 提取 exe
        - 使用 pyinstxtractor 从 PyInstaller 打包的 exe 中提取 Python 文件
        - 提取出 .pyc 字节码文件和依赖库
        - 输出目录: exe文件_extracted/
    
    步骤2: 反编译字节码
        - 使用 uncompyle6/decompyle3/pycdc 将 .pyc 转换为 .py
        - 自动尝试多种反编译工具
        - 输出目录: decompiled/
    
    步骤3: 分析授权机制
        - 搜索授权相关代码
        - 生成分析报告
        - 提取关键代码
    
    步骤4: 生成注册机
        - 根据分析结果编写注册机
        - 支持多种常见授权算法
        - 交互式生成授权码
    
    【文件说明】
    
    - 1_extract_pyinstaller.py: 提取工具
    - 2_decompile_pyc.py: 反编译工具
    - 3_analyze_license.py: 分析工具
    - 4_crack_keygen.py: 注册机
    - README_逆向指南.txt: 详细说明文档
    
    【注意事项】
    
    1. 需要安装的工具:
       pip install pyinstxtractor uncompyle6 decompyle3
    
    2. 某些步骤可能失败:
       - Python 版本不匹配
       - 代码混淆
       - 反编译工具不支持
    
    3. 法律声明:
       本工具仅供学习和安全研究，请勿用于非法用途
    
    按 Enter 返回主菜单...
    """
    print(help_text)
    input()

def main():
    """主函数"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            manual_mode()
        elif choice == '2':
            quick_mode()
        elif choice == '3':
            interactive_mode()
        elif choice == '4':
            show_help()
            continue
        elif choice == '0':
            print("\n[*] 退出程序")
            break
        else:
            print("\n[!] 无效选择，请重试")
            time.sleep(1)
            continue
        
        if input("\n\n按 Enter 返回主菜单 (或输入 q 退出): ").lower() == 'q':
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] 用户中断")
    except Exception as e:
        print(f"\n[!] 发生错误: {e}")
        import traceback
        traceback.print_exc()
