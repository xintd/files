import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as sd
from datetime import datetime

import requests

GP_CONFIG_FILE = './.txt'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

A1_TIME = datetime.strptime('09:15:00', TIME_FORMAT).time()  # 开市时间
A2_TIME = datetime.strptime('11:30:00', TIME_FORMAT).time()
P1_TIME = datetime.strptime('13:00:00', TIME_FORMAT).time()
P2_TIME = datetime.strptime('15:00:00', TIME_FORMAT).time()

last_update_time = None
cached_result = None
_GP_CODES_CACHE = None
update_interval = 800


def search(gp_dm):
    if not gp_dm:
        return ''
    """
    查询多只的实时行情
    :param gp_dm: 代码列表
    :return: 返回查询结果
    """
    global last_update_time, cached_result

    # 如果上次更新时间不为空，并且当前时间与上次更新时间在同一天，
    # 并且现在不是开市时间，则直接返回缓存的查询结果。
    if (last_update_time is not None and
            last_update_time.date() == datetime.now().date() and
            not (is_worktime() and is_workday())):
        return cached_result

    codes = ','.join(gp_dm)
    url = f'https://qt.gtimg.cn/q={codes}'
    resp = requests.get(url)
    rest = [x.strip().split('~') for x in resp.text.split('\n') if x.strip()]
    res = ''.join([f"{i[1]}: {i[3]}[{i[32]}]\n" for i in rest])

    # 更新上次更新时间和缓存的查询结果。
    last_update_time = datetime.now()
    cached_result = res

    return res


def add_prefix(code):
    return f'sh{code}' if code.startswith('60') else f'sz{code}' if not ('sh' in code or 'sz' in code) else code


def get_gp_codes(reload=False):
    """
    获取代码列表
    :param reload: 是否需要重新加载配置文件
    """
    global _GP_CODES_CACHE
    if _GP_CODES_CACHE is None or reload:
        with open(GP_CONFIG_FILE, 'r') as f:
            gp_list = [line.strip() for line in f]

        # 过滤空行和注释行
        gp_list = [line for line in gp_list if line and not line.startswith('#')]
        _GP_CODES_CACHE = gp_list
    return list(map(add_prefix, _GP_CODES_CACHE))


def is_workday():
    """
    检查今天是否是工作日
    :return: 如果是工作日返回True，否则返回False
    """
    today = datetime.now().weekday()
    return today < 5


def is_worktime():
    """
    检查现在是否是开市时间
    :return: 如果是开市时间返回True，否则返回False
    """
    now = datetime.now().time()
    if now < A1_TIME:
        return False
    elif now <= A2_TIME:
        return True
    elif now < P1_TIME:
        return False
    elif now <= P2_TIME:
        return True
    else:
        return False


class FloatingWindow:
    """
    带有拖拽功能的窗口
    """

    def __init__(self, rt):
        self.rt = rt
        self.x = 0
        self.y = 0

        lb.bind("<ButtonPress-1>", self.start_move)
        lb.bind("<ButtonRelease-1>", self.stop_move)
        lb.bind("<Motion>", self.on_motion)

        self.is_moving = False  # 是否正在移动
        self.update_enabled = True  # 标签内容更新是否可用

    def start_move(self, event):
        self.toggle_update(False)  # 暂停标签内容更新
        self.is_moving = True
        self.x, self.y = event.x, event.y

    def stop_move(self, event):
        self.is_moving = False
        self.toggle_update(True)  # 恢复标签内容更新

    def on_motion(self, event):
        """
        移动窗口
        """
        if self.is_moving:
            new_x = self.rt.winfo_x() + (event.x - self.x)
            new_y = self.rt.winfo_y() + (event.y - self.y)
            self.rt.geometry(f'+{new_x}+{new_y}')

    def toggle_update(self, enabled):
        """
        启用或禁用标签内容更新
        :param enabled: 是否启用
        """
        self.update_enabled = enabled
        if enabled:
            update_label()
        else:
            root.after_cancel(self.update_id)


def update_label():
    """
    更新标签内容
    """
    text = f"{datetime.now().date()} 今天休市\n{search(get_gp_codes())}" if not is_workday() else (
        f"{datetime.now().strftime(DATETIME_FORMAT)}\n{search(get_gp_codes())}" if is_worktime() else
        f"{datetime.now().date()} 已休市\n{search(get_gp_codes())}"
    )

    lb.configure(state='normal')  # 激活文本框编辑状态
    lb.tag_configure("center", justify="center")
    lb.delete('1.0', tk.END)  # 清空文本框内容
    lb.insert(tk.END, text.strip(), 'center')  # 插入新内容

    # 按行设置文本颜色
    for i, line in enumerate(text.split('\n')):
        fg_color = 'red' if ('[' in line and float(line.split('[')[1].strip()[:-1]) > 0) else 'green' if (
                '[' in line) else 'black'
        lb.tag_add(f'tag{i}', f'{i + 1}.0', f'{i + 1}.end')
        lb.tag_config(f'tag{i}', foreground=fg_color)

    lb.configure(state='disabled')  # 禁用文本框编辑状态
    # 将标识符赋值给类属性
    FloatingWindow.update_id = root.after(update_interval, update_label)


def exit_app():
    """
    退出应用程序
    """
    root.quit()


if __name__ == '__main__':
    root = tk.Tk()
    root.overrideredirect(True)  # 无标题栏窗体
    root.attributes('-alpha', 0.3)
    width = 150
    height = int(17.3 * (len(get_gp_codes()) + 1))
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口左上角坐标
    x = int(screen_width - width)
    y = int(screen_height - height)
    # 设置窗口位置
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", "gray")


    def update_gp_codes(codes):
        """
        更新代码到配置文件
        :param codes: 代码列表
        """
        with open(GP_CONFIG_FILE, 'a') as f:
            for code in codes:
                f.write('\n' + code)


    def add_stock():
        """
        添加股票代码
        """
        codes = sd.askstring("添加", "请输入，多个用逗号隔开：")
        if codes:
            codes = [code.strip() for code in codes.split(',')]
            # 检查这些股票代码是否已经存在于配置文件中
            with open(GP_CONFIG_FILE, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
            new_codes = [code for code in codes if code not in lines]
            if new_codes:
                update_gp_codes(new_codes)
                height = int(17.3 * (len(get_gp_codes(True)) + 1))
                root.geometry(f'{width}x{height}')
                # 更新标签内容
                global last_update_time
                last_update_time = None
                update_label()


    def delete_stock():
        """
        删除股票代码
        """
        codes = sd.askstring("删除", "请输入，多个用逗号隔开：")
        if codes:
            codes = [code.strip() for code in codes.split(',')]
            with open(GP_CONFIG_FILE, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
            # 过滤空行和注释行
            lines = [line for line in lines if line and not line.startswith('#')]
            # 删除指定代码
            deleted_codes = []
            for code in codes:
                if code in lines:
                    lines.remove(code)
                    deleted_codes.append(code)
            # 写回到配置文件
            with open(GP_CONFIG_FILE, 'w') as f:
                f.write('\n'.join(lines))
            height = int(17.3 * (len(get_gp_codes(True)) + 1))
            root.geometry(f'{width}x{height}')
            # 更新标签内容
            global last_update_time
            last_update_time = None
            update_label()


    def update_interval_handler(update_interval_init=800):
        interval = sd.askstring("更新间隔", "请输入更新间隔（毫秒）：", initialvalue=update_interval_init)
        if interval:
            try:
                int(interval)
            except ValueError:
                # 如果输入的不是整数，则提示用户重新输入
                msgbox.showerror("错误", "请输入一个整数")
            else:
                if int(interval) < 800:
                    msgbox.showerror("错误", "更新间隔不能小于800")
                else:
                    # 否则更新更新间隔，并重新开始更新标签内容
                    global update_interval
                    update_interval = int(interval)
                    root.after_cancel(root.floater.update_id)
                    root.floater.update_id = root.after(update_interval, update_label)


    # 添加右键菜单
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="设置更新间隔", command=lambda: update_interval_handler())
    topmost_var = tk.BooleanVar(value=True)  # 初始选中置顶
    menu.add_radiobutton(label="置顶", variable=topmost_var, value=True,
                         command=lambda: root.attributes("-topmost", True))
    menu.add_radiobutton(label="取消置顶", variable=topmost_var, value=False,
                         command=lambda: root.attributes("-topmost", False))
    menu.add_command(label="增加透明度",
                     command=lambda: root.attributes("-alpha", min(1, root.attributes('-alpha') + 0.2)))
    menu.add_command(label="减小透明度",
                     command=lambda: root.attributes("-alpha", max(0.1, root.attributes('-alpha') - 0.2)))
    menu.add_separator()
    menu.add_command(label="添加", command=add_stock)
    menu.add_command(label="删除", command=delete_stock)
    menu.add_separator()
    menu.add_command(label="退出", command=exit_app)


    def popup(event):
        menu.post(event.x_root, event.y_root)


    root.bind("<Button-3>", popup)

    lb = tk.Text(root, font=("微软雅黑", 9))
    lb.pack(fill='both', side='top')

    root.floater = FloatingWindow(root)
    update_label()

    root.mainloop()