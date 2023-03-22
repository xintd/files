import tkinter as tk
import requests
from datetime import datetime

GP_CONFIG_FILE = './.txt'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'

A1_TIME = datetime.strptime('09:15:00', TIME_FORMAT).time()  # 开市时间
A2_TIME = datetime.strptime('11:30:00', TIME_FORMAT).time()
P1_TIME = datetime.strptime('13:00:00', TIME_FORMAT).time()
P2_TIME = datetime.strptime('15:00:00', TIME_FORMAT).time()

last_update_time = None
cached_result = None


def search(gp_dm):
    """
    查询多只股票的实时行情
    :param gp_dm: 股票代码列表
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


def get_gp_codes():
    """
    从配置文件中读取股票代码
    :return: 股票代码列表
    """
    with open(GP_CONFIG_FILE, 'r') as f:
        gp_list = [line.strip() for line in f]

    # 过滤空行和注释行
    gp_list = [line for line in gp_list if line and not line.startswith('#')]

    if not gp_list:
        raise ValueError(f'未在配置文件 "{GP_CONFIG_FILE}" 中找到股票代码')

    return list(map(add_prefix, gp_list))


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
        self.x = event.x
        self.y = event.y
        self.is_moving = True

    def stop_move(self, event):
        self.x = None
        self.y = None
        self.is_moving = False
        self.toggle_update(True)  # 恢复标签内容更新

    def on_motion(self, event):
        if not self.is_moving:
            return

        # 计算窗口的新位置
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.rt.winfo_x() + deltax
        y = self.rt.winfo_y() + deltay

        # 更新窗口位置
        self.rt.geometry(f"+{x}+{y}")

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
    FloatingWindow.update_id = root.after(1000, update_label)


def exit_app():
    """
    退出应用程序
    """
    root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.overrideredirect(True)  # 无标题栏窗体
    root.attributes('-alpha', 0.2)
    width = 150
    height = 9 + 16 * (len(get_gp_codes()) + 1)
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口左上角坐标
    x = int(screen_width - width)
    y = int(screen_height - height)
    # 设置窗口位置
    root.geometry(f'{width}x{height}+0+0')
    root.geometry("+{}+{}".format(x, y))
    root.attributes("-topmost", 1)

    root.wm_attributes("-transparentcolor", "gray")

    # 添加右键菜单
    right_click_menu = tk.Menu(root, tearoff=False)
    right_click_menu.add_command(label="退出", command=exit_app)


    def popup(event):
        right_click_menu.post(event.x_root, event.y_root)


    root.bind("<Button-3>", popup)

    lb = tk.Text(root, font=("微软雅黑", 9))
    lb.pack(fill='both', side='top')

    root.floater = FloatingWindow(root)
    update_label()

    root.mainloop()
