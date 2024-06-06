import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import subprocess
import time

class CharacterWindow:
    def __init__(self, master, image_path):
        self.master = master
        self.master.overrideredirect(True)  # 隐藏窗口装饰

        # 加载并缩放人物图片
        self.original_image = Image.open(image_path)
        self.scaled_image = self.original_image.resize(
            (int(self.original_image.width * 0.15), int(self.original_image.height * 0.15)), Image.LANCZOS
        )
        self.character_photo = ImageTk.PhotoImage(self.scaled_image)

        # 创建Label显示人物图片
        self.label = tk.Label(master, image=self.character_photo)
        self.label.pack()

        # 创建右键菜单
        self.context_menu = tk.Menu(master, tearoff=0)
        self.context_menu.add_command(label="输入任务", command=self.show_input_dialog)
        self.context_menu.add_command(label="退出", command=self.exit_program)
        self.label.bind("<Button-3>", self.show_context_menu)

        # 设置窗口背景透明
        self.master.attributes('-transparentcolor', 'white')

        # 设置窗口始终保持在桌面最顶层
        self.master.attributes('-topmost', True)

        # 绑定鼠标事件以实现拖动功能
        self.label.bind('<Button-1>', self.start_move)
        self.label.bind('<B1-Motion>', self.do_move)

        # 绑定鼠标双击事件来触发语音播报
        self.label.bind('<Double-Button-1>', self.on_double_click)

        # 初始化 robot 进程
        self.robot_process = None

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.master.winfo_pointerx() - self.x
        y = self.master.winfo_pointery() - self.y
        self.master.geometry(f"+{x}+{y}")

    #双击以启动robot.exe
    def on_double_click(self, event):
        self.robot_process = subprocess.Popen(['robot.exe'])

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    #send_message函数，用来发送消息给robot，用来插入任务
    def send_message(self, message, delay):
        process = subprocess.Popen(["robot.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # 向C++程序发送消息和时间
        input_data = f"{message}\n{delay}\n"
        input_data_encoded = input_data.encode('utf-16')
        input_data_str = input_data_encoded.decode('utf-16')  # 解码为字符串
        process.stdin.write(input_data_str)
        process.stdin.flush()
        output_message = process.stdout.readline().rstrip()
        print("Output from C++ program:", output_message)
        process.wait()


    def show_input_dialog(self):
        # 创建弹出对话框以输入消息和时间戳
        message = simpledialog.askstring("输入任务消息", "消息:")
        if message:
            timestamp_str = simpledialog.askstring("输入任务时间戳", "时间戳（秒）:")
            if timestamp_str:
                try:
                    delay = int(timestamp_str)
                    self.send_message(message, delay)
                except ValueError:
                    messagebox.showerror("输入错误", "时间戳必须是整数")

    def exit_program(self):
        # 退出程序时终止 robot 进程
        if self.robot_process:
            self.robot_process.terminate()
        self.master.quit()

if __name__ == "__main__":
    # 创建Tkinter窗口
    root = tk.Tk()

    # 设置人物图片路径
    image_path = "robot.jpg"  # 替换为你的人物图片路径

    # 加载图片并缩放
    original_image = Image.open(image_path)
    scaled_image = original_image.resize(
        (int(original_image.width * 0.15), int(original_image.height * 0.15)), Image.LANCZOS
    )
    window_width, window_height = scaled_image.size

    # 设置窗口位置和大小（居中显示）
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - window_width - 100  # 10个像素的边距
    y = screen_height - window_height - 500  # 50个像素的边距，留出任务栏的位置
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 创建CharacterWindow对象
    character_window = CharacterWindow(root, image_path)

    # 运行窗口
    root.mainloop()
