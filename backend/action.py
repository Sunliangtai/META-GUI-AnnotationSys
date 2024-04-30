import requests
from io import BytesIO
from PIL import Image
import subprocess
import time

IdToApp = {}
ActionType = ["click", "scroll", "typing", "page", "back", 'screen', 'layout', 'clear', 'read', 'enter', 'home']


class Server:
    def __init__(self, port, emulator):
        self.port = port
        self.emulator = emulator

    def click(self, pos):
        pos = tuple(map(int, pos.split(",")))
        action_seq = f"adb -s {self.emulator} shell input tap {pos[0]} {pos[1]}"
        excute(action_seq, wait=True)

        return "ok"

    def scroll(self, pos=None, poss=None):
        pos = tuple(map(int, pos.split(",")))
        if poss in ['0', '1', '2', '3']:
            action_seq = f"adb -s {self.emulator} shell wm size"
            screen_size = excute(action_seq, wait=True, out=True).split(b'\n')[1].split(b' ')[
                -1].split(b'x')
            width = int(screen_size[0])
            height = int(screen_size[1])
            if poss == '0':
                action_seq = f"adb -s {self.emulator} shell input swipe {pos[0]} {pos[1]} {pos[0]} 0 200"
                excute(action_seq, wait=True)
            elif poss == '1':
                action_seq = f"adb -s {self.emulator} shell input swipe {pos[0]} {pos[1]} {pos[0]} {height} 200"
                excute(action_seq, wait=True)
            elif poss == '2':
                action_seq = f"adb -s {self.emulator} shell input swipe {pos[0]} {pos[1]} 0 {pos[1]} 200"
                excute(action_seq, wait=True)
            elif poss == '3':
                action_seq = f"adb -s {self.emulator} shell input swipe {pos[0]} {pos[1]} {width} {pos[1]} 200"
                excute(action_seq, wait=True)
        else:
            poss = tuple(map(int, poss.split(",")))
            action_seq = f"adb -s {self.emulator} shell input swipe {pos[0]} {pos[1]} {poss[0]} {poss[1]} 200"
            excute(action_seq, wait=True)

        return "ok"

    def typing(self, text):
        text = text.replace(" ", "%s")
        print(text)
        action_seq = f'adb -s {self.emulator} shell input text "{text}"'
        excute(action_seq, wait=True)

        return "ok"

    def page(self, pos):
        action_seq = f"adb -s {self.emulator} shell wm size"
        screen_size = excute(action_seq, wait=True, out=True).split(b'\n')[1].split(b' ')[-1].split(
            b'x')
        width = int(screen_size[0])
        height = int(screen_size[1])
        if pos == "0":
            action_seq = f"adb -s {self.emulator} shell input swipe {width // 2} {height - 2} {width // 2} {2}"
            excute(action_seq, wait=True)
        elif pos == "1":
            action_seq = f"adb -s {self.emulator} shell input swipe {width // 2} {2} {width // 2} {height - 2}"
            excute(action_seq, wait=True)
        elif pos == "2":
            action_seq = f"adb -s {self.emulator} shell input swipe {width - 2} {height // 2} {2} {height // 2}"
            excute(action_seq, wait=True)
        elif pos == "3":
            action_seq = f"adb -s {self.emulator} shell input swipe {2} {height // 2} {width - 2} {height // 2}"
            excute(action_seq, wait=True)

        return "ok"

    def back(self):
        action_seq = f"adb -s {self.emulator} shell input keyevent 4"
        excute(action_seq, wait=True)

        return "ok"

    def home(self):
        action_seq = f"adb -s {self.emulator} shell input keyevent 3"
        excute(action_seq, wait=True)

        return "ok"

    def screen(self):
        start = time.time()
        action_seq = f"adb -s {self.emulator} exec-out screencap -p"
        img = excute(action_seq, wait=True, out=True)
        end = time.time()
        print(end - start)
        return img

    def layout(self):
        dump_action_seq = f"adb -s {self.emulator} shell uiautomator dump"
        count = 0
        flag = True
        while True:
            count += 1
            err = excute(dump_action_seq, wait=True, err=True)
            if count > 5:
                flag = False
                break
            if err is None:
                print("return is None!")
                continue
            else:
                err = err.decode("utf-8")
            if "ERROR" in err:
                print(err)
                continue
            break
        if not flag:
            return """<hierarchy rotation="0">
<node index="0" text="ErrorFlag" resource-id="" class="android.widget.FrameLayout" package="com.google.android.googlequicksearchbox" content-desc="" checkable="false" checked="false" clickable="false" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[0,0][1440,2392]"> </node>
</hierarchy>"""
        pull_action_seq = f"adb -s {self.emulator} shell cat /sdcard/window_dump.xml"
        print("execute for %d times" % count)
        layout_xml = excute(pull_action_seq, wait=True, out=True)
        return layout_xml.decode()

    def clear(self):
        delete = ["67"] * 250
        action_seq = f"adb -s {self.emulator} shell input keyevent --longpress {' '.join(delete)}"
        excute(action_seq, wait=True)

        return "ok"

    def enter(self):
        action_seq = f"adb -s {self.emulator} shell input keyevent KEYCODE_ENTER"
        excute(action_seq, wait=True)

        return "ok"

    def process(self, action, pos, text):
        print("process", action)
        if action not in ActionType:
            return "ActionType Error"
        if action == "click":
            return self.click(pos)
        elif action == "scroll":
            return self.scroll(pos, text)
        elif action == "typing":
            return self.typing(text)
        elif action == "page":
            return self.page(text)
        elif action == "back":
            return self.back()
        elif action == "screen":
            return self.screen()
        elif action == "layout":
            return self.layout()
        elif action == "clear":
            return self.clear()
        elif action == "read":
            return "ok"
        elif action == "enter":
            return self.enter()
        elif action == "home":
            return self.home()


"""
    cmd example:
        id|action|pos|text
    Important:
        No space !!!
"""


def excute(order, inputs='', pre='', wait=False, out=False, err=False):
    if pre == '':
        p = subprocess.Popen(args=order, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    else:
        line = '%s "%s"' % (pre, order)
        p = subprocess.Popen(args=line, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    if inputs == '':
        if wait:
            out, err = p.communicate()
    else:
        p.stdin.write(bytes(inputs, encoding="gb2312"))
        if wait:
            out, err = p.communicate()
    if err:
        return err
    if out:
        return out


class Action:
    def __init__(self, action_type, pos_x=None, pos_y=None, text=None):
        self.type = action_type
        self.x = pos_x
        self.y = pos_y
        self.text = text

    def parse(self, uid):
        if self.x is None or self.y is None:
            if self.text is None:
                return f"{uid}|{self.type}|NULL|NULL"
            else:
                return f"{uid}|{self.type}|NULL|{self.text}"
        else:
            if self.text is None:
                return f"{uid}|{self.type}|{self.x},{self.y}|NULL"
            else:
                return f"{uid}|{self.type}|{self.x},{self.y}|{self.text}"


"""
    Example:
        CLICK: Action("click", 128, 256, None)
            点击(128,256)坐标位置的组件
        SCROLL: Action("scroll", 128, 256, text)
            if text in ["0", "1", "2", "3"]:
                意味着从(128,256)坐标位置滑倒屏幕边缘，0上滑，1下滑，2左滑，3右滑
            if text is sample like "256,512":
                意味着从(128,256)坐标位置滑倒(256,512)坐标位置
        TYPING: Action("typing", 128, 256, "ok")
            会自动利用XML搜索(128,256)坐标位置可编辑的组件，并输入"ok"
        PAGE: Action("page", None, None, text)
            text in ["0", "1", "2", "3"]:
                意味着整个界面的滑动，0上滑，1下滑，2左滑，3右滑
        BACK: Action("back", None, None, None)
            返回上一步
        SCREEN: Action("screen", None, None, None)
            获取屏幕截图(用户不可见)
"""


def perform(cmd):
    cmd_sp = cmd.split('|')
    usr_id = cmd_sp[0]
    port = 4274
    emulator = EMULATOR
    if usr_id in IdToApp.keys():
        server: Server = IdToApp[usr_id]
    else:
        server = Server(port, emulator)
        IdToApp[usr_id] = server
    return server.process(cmd_sp[1].lower(), cmd_sp[2].lower(), cmd_sp[3].lower())


def parse_img(uid):
    cmd = f"{uid}|SCREEN|NULL|NULL"
    cmd_sp = cmd.split('|')
    usr_id = cmd_sp[0]
    port = 4274
    emulator = EMULATOR
    if usr_id in IdToApp.keys():
        server: Server = IdToApp[usr_id]
    else:
        server = Server(port, emulator)
        IdToApp[usr_id] = server
    content = server.process(cmd_sp[1].lower(), cmd_sp[2].lower(), cmd_sp[3].lower())
    io_stream = BytesIO(content)
    img = Image.open(fp=io_stream)
    # img = img.resize([int(img.size[0]*0.25), int(img.size[1]*0.25)])
    return img


def parse_layout(uid):
    cmd = f"{uid}|LAYOUT|NULL|NULL"
    cmd_sp = cmd.split('|')
    usr_id = cmd_sp[0]
    port = 4274
    emulator = EMULATOR
    if usr_id in IdToApp.keys():
        server: Server = IdToApp[usr_id]
    else:
        server = Server(port, emulator)
        IdToApp[usr_id] = server
    content = server.process(cmd_sp[1].lower(), cmd_sp[2].lower(), cmd_sp[3].lower())
    return content


start_action_seq = f"adb devices"
pid = excute(start_action_seq, wait=True, out=True).decode()
pid = pid.split('\n')[1].split('\t')[0]

EMULATOR = pid
