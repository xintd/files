import os
import sched
import threading
import time
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as sd
from datetime import datetime, date

import requests

GP_CONFIG_FILE = './.txt'

last_update_time = None
cached_result = None
update_interval = 800


def _search(s):
    last_request_time = time.time()  # 记录上一个请求的执行时间
    if not _GP_CODES_CACHE:
        update_label('')
    else:
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
                not (worktime and workday)):
            update_label(cached_result)
        else:
            codes = ','.join(_GP_CODES_CACHE)
            url = f'https://qt.gtimg.cn/q={codes}'
            resp = requests.get(url)
            rest = [detail.strip().split('~') for detail in resp.text.splitlines() if detail.strip()]
            res = ''.join([f"{i[1]}: {i[3]}[{i[32]}]\n" for i in rest])
            # 更新上次更新时间和缓存的查询结果。
            last_update_time = datetime.now()
            cached_result = res
            update_label(res)
    elapsed_time = time.time() - last_request_time
    remaining_time = max(0.0, update_interval / 1000 - elapsed_time)
    s.enter(remaining_time, 9, _search, (s,))


def add_prefix(code):
    return f'sh{code}' if code.startswith('60') else f'sz{code}' if not ('sh' in code or 'sz' in code) else code


def get_gp_codes(reload=False):
    """
    获取代码列表
    :param reload: 是否需要重新加载配置文件
    """
    global _GP_CODES_CACHE, last_update_time
    if reload or not _GP_CODES_CACHE:
        last_update_time = None
        with open(GP_CONFIG_FILE, 'r') as f:
            gp_list = [line.strip() for line in f]

        # 过滤空行和注释行
        gp_list = [line for line in gp_list if line and not line.startswith('#')]
        _GP_CODES_CACHE = list(map(add_prefix, gp_list))
    return _GP_CODES_CACHE


def is_workday():
    """
    检查今天是否是工作日
    :return: 如果是工作日返回True，否则返回False
    """
    today = datetime.now().weekday()
    return today < 5


def is_worktime(s):
    time_format = '%H:%M:%S'
    a1_time = datetime.strptime('09:15:00', time_format).time()  # 开市时间
    a2_time = datetime.strptime('11:30:00', time_format).time()
    p1_time = datetime.strptime('13:00:00', time_format).time()
    p2_time = datetime.strptime('15:00:00', time_format).time()
    """
    检查现在是否是开市时间
    :return: 如果是开市时间返回True，否则返回False
    """
    now = datetime.now().time()
    if now < a1_time:
        is_work_time = False
        time_interval = max(1, combine(now, a1_time) - 10)
    elif now <= a2_time:
        is_work_time = True
        time_interval = combine(now, a2_time) + 10
    elif now < p1_time:
        is_work_time = False
        time_interval = max(1, combine(now, p1_time) - 10)
    elif now <= p2_time:
        is_work_time = True
        time_interval = combine(now, p2_time) + 10
    else:
        is_work_time = False
        max_time = datetime.strptime('23:59:59', time_format).time()
        time_interval = combine(now, max_time)
    global worktime
    worktime = is_work_time
    s.enter(time_interval, 0, is_worktime, (s,))


def combine(now, target_time):
    now = datetime.combine(date.today(), now)
    target_time = datetime.combine(date.today(), target_time)
    diff = target_time - now
    return int(diff.total_seconds())


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

    def start_move(self, event):
        self.is_moving = True
        self.x, self.y = event.x, event.y

    def stop_move(self, event):
        self.is_moving = False

    def on_motion(self, event):
        """
        移动窗口
        """
        if self.is_moving:
            new_x = self.rt.winfo_x() + (event.x - self.x)
            new_y = self.rt.winfo_y() + (event.y - self.y)
            self.rt.geometry(f'+{new_x}+{new_y}')


def update_label(data):
    datetime_format = '%Y/%m/%d %H:%M:%S'

    # build the label content with workday/worktime status
    now = datetime.now()
    if not workday:
        text = f"{now.date()} 今天休市\n{data}"
    elif not worktime:
        text = f"{now.date()} 已休市\n{data}"
    else:
        text = f"{now.strftime(datetime_format)}\n{data}"

    content = lb.get('1.0', tk.END)
    if '休市' in content.strip():
        return

    # split data into lines
    lines = text.strip().splitlines()

    # determine the foreground color for each line
    fg_colors = []
    for line in lines:
        if '[' not in line:
            fg_colors.append('black')
        else:
            change_percent = float(line.split('[')[1].strip()[:-1])
            fg_color = 'green' if change_percent <= 0 else 'red'
            fg_colors.append(fg_color)

    # update the label content with selective delete and insert
    lb.configure(state='normal')
    lb.tag_configure("center", justify="center")
    lb.delete('1.0', tk.END)  # 清空文本框内容
    lb.insert(tk.END, text.strip(), 'center')  # 插入新内容
    for i in range(len(lines)):
        lb.tag_add(f'tag{i}', f'{i + 1}.0', f'{i + 1}.end')
        lb.tag_config(f'tag{i}', foreground=fg_colors[i])
    lb.configure(state='disabled')  # 禁用文本框编辑状态


def exit_app():
    """
    退出应用程序
    """
    root.quit()


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
            height_add = int(17.3 * (len(get_gp_codes(True)) + 1))
            root.geometry(f'{width}x{height_add}')


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
        for code in codes:
            if code in lines:
                lines.remove(code)
        # 写回到配置文件
        with open(GP_CONFIG_FILE, 'w') as f:
            f.write('\n'.join(lines))
        height_del = int(17.3 * (len(get_gp_codes(True)) + 1))
        root.geometry(f'{width}x{height_del}')


def update_interval_handler():
    global update_interval
    interval = sd.askstring("更新间隔", "请输入更新间隔（毫秒）：", initialvalue=str(update_interval))
    if interval:
        try:
            int(interval)
        except ValueError:
            # 如果输入的不是整数，则提示用户重新输入
            msgbox.showerror("错误", "请输入一个整数")
        else:
            if int(interval) < 800:
                msgbox.showerror("错误", "更新间隔不能小于800")
                update_interval = 800
            else:
                # 否则更新更新间隔，并重新开始更新标签内容
                update_interval = int(interval)


if __name__ == '__main__':
    if not os.path.exists(GP_CONFIG_FILE):
        open(GP_CONFIG_FILE, 'a').close()

    root = tk.Tk()
    root.overrideredirect(True)  # 无标题栏窗体
    root.attributes('-alpha', 0.3)
    width = 150
    _GP_CODES_CACHE = []
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

    # 启动定时任务，第一次立即执行
    workday = is_workday()
    worktime = False

    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 0, is_worktime, (s,))
    s.enter(0, 0, _search, (s,))

    # 在另一个线程中启动服务器并运行 tkinter 主循环
    t = threading.Thread(target=s.run)
    t.start()

    root.mainloop()
