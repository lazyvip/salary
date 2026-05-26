import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import re

INDEX_PATH = Path(__file__).resolve().parents[1] / 'site' / 'index.html'

def read_current_password():
    if not INDEX_PATH.exists():
        return None
    text = INDEX_PATH.read_text(encoding='utf-8')
    m = re.search(r'<meta\s+name="site-password"\s+content="([^"]*)"', text)
    return m.group(1) if m else ''

def update_password(pwd: str):
    if not INDEX_PATH.exists():
        messagebox.showerror('错误', f'未找到 index.html\n{INDEX_PATH}')
        return False
    if any(ch in pwd for ch in ['"', '<', '>']):
        messagebox.showerror('错误', '密码不能包含 " < >')
        return False
    text = INDEX_PATH.read_text(encoding='utf-8')
    pattern = r'(<meta\s+name="site-password"\s+content=")[^"]*("\s*/?>)'
    if re.search(pattern, text):
        text = re.sub(pattern, lambda m: f'{m.group(1)}{pwd}{m.group(2)}', text)
    else:
        head_close = text.find('</head>')
        if head_close != -1:
            inject = f'    <meta name="site-password" content="{pwd}">\n'
            text = text[:head_close] + inject + text[head_close:]
        else:
            messagebox.showerror('错误', 'index.html 缺少 </head>，无法写入密码')
            return False
    INDEX_PATH.write_text(text, encoding='utf-8')
    return True

def remove_password():
    if not INDEX_PATH.exists():
        messagebox.showerror('错误', f'未找到 index.html\n{INDEX_PATH}')
        return False
    text = INDEX_PATH.read_text(encoding='utf-8')
    text = re.sub(r'\s*<meta\s+name="site-password"\s+content="[^"]*"\s*/?>\s*\n?', '\n', text)
    INDEX_PATH.write_text(text, encoding='utf-8')
    return True

def main():
    root = tk.Tk()
    root.title('设置访问密码')
    root.geometry('340x200')
    root.resizable(False, False)

    current = read_current_password()
    status_text = f'当前密码：{current}' if current else '当前未设置密码'
    status = tk.Label(root, text=status_text, fg='#666')
    status.pack(pady=(12, 4))

    tk.Label(root, text='新密码：').pack()
    entry = tk.Entry(root, show='*')
    entry.pack(fill='x', padx=20)

    def refresh_status():
        c = read_current_password()
        status.config(text=f'当前密码：{c}' if c else '当前未设置密码')

    def on_save():
        pwd = entry.get().strip()
        if not pwd:
            messagebox.showwarning('提示', '请输入密码')
            return
        if update_password(pwd):
            messagebox.showinfo('完成', '密码已更新')
            refresh_status()
            entry.delete(0, tk.END)

    def on_clear():
        if not read_current_password():
            messagebox.showinfo('提示', '当前未设置密码')
            return
        if messagebox.askyesno('确认', '确定要清除密码吗？\n清除后任何人都可以直接访问。'):
            if remove_password():
                messagebox.showinfo('完成', '密码已清除')
                refresh_status()
                entry.delete(0, tk.END)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=12)
    tk.Button(btn_frame, text='保存', command=on_save, width=8).pack(side='left', padx=6)
    tk.Button(btn_frame, text='清除密码', command=on_clear, width=8).pack(side='left', padx=6)

    root.mainloop()

if __name__ == '__main__':
    main()
