import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import re

INDEX_PATH = Path(__file__).resolve().parents[1] / 'site' / 'index.html'

def update_password(pwd: str):
    if not INDEX_PATH.exists():
        messagebox.showerror('错误', f'未找到 index.html\n{INDEX_PATH}')
        return False
    if any(ch in pwd for ch in ['"', '<', '>']):
        messagebox.showerror('错误', '密码不能包含 " < >')
        return False
    text = INDEX_PATH.read_text(encoding='utf-8')
    pattern = r'(<meta\s+name="site-password"\s+content=")[^"]*("\s*>)'
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

def main():
    root = tk.Tk()
    root.title('设置访问密码')
    root.geometry('320x140')
    tk.Label(root, text='新密码：').pack(pady=8)
    entry = tk.Entry(root, show='*')
    entry.pack(fill='x', padx=16)
    def on_save():
        pwd = entry.get().strip()
        if not pwd:
            messagebox.showwarning('提示', '请输入密码')
            return
        if update_password(pwd):
            messagebox.showinfo('完成', '密码已更新')
    tk.Button(root, text='保存', command=on_save).pack(pady=12)
    root.mainloop()

if __name__ == '__main__':
    main()
