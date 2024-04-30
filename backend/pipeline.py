import json
import os
from typing import List

from utils import read_file, read_json, write_json, write_file
from collections import namedtuple

Transform = namedtuple("Transform", ["trigger", "next_state", "leave"])


class Event:
    def __init__(self, query, data=None):
        self.query = query
        self.data = data


class Response:
    def __init__(self, res, actions=None):
        self.res = res
        self.actions = actions

    def __repr__(self):
        return self.res

    def __str__(self):
        return self.res


class Pipeline:
    def __init__(self):
        self.state = "init"
        self.transform = self.transform_from_init()
        self.world = {}
        self.response = Response("")

    def __repr__(self):
        return self.response.res

    def change_state(self, event: Event):
        for trans in self.transform:
            if trans.trigger(event):
                trans.leave(event)
                self.state = trans.next_state
                print("===LOG===: Change to {}".format(trans.next_state))
                return

    def __call__(self, query, data=None):
        print(">>", query)
        if query == "reset":
            self.state = "init"
            self.enter_init()
            return
        event = Event(query, data)
        self.change_state(event)
        self.enter()

    def enter(self):
        if self.state == "init":
            self.enter_init()
        elif self.state == "record_trigger":
            self.enter_record_trigger()
        elif self.state == "record_actions":
            self.enter_record_actions()
        elif self.state == "record_name":
            self.enter_record_name()
        elif self.state == "record":
            self.enter_record()
        elif self.state == "new_task":
            self.enter_new_task()
        elif self.state == "bind_task":
            self.enter_bind_task()
        elif self.state == "bind":
            self.enter_bind()
        elif self.state == "task_not_found":
            self.enter_task_not_found()
        elif self.state == "task":
            self.enter_task()

    def do_nothing(self, *args, **kwargs):
        pass

    """
    init
    """

    def before_init(self, event):
        self.world["before_init"] = event.query

    def enter_init(self):
        self.response = Response("你好，输入录制开始录制新任务，或者直接输入需要执行的任务。")
        self.transform = self.transform_from_init()
        before_init = None
        if "before_init" in self.world:
            before_init = self.world["before_init"]
        self.world = {}
        if before_init is not None:
            self(before_init, None)

    def transform_from_init(self):
        return [
            Transform(trigger=lambda e: e.query == "录制", next_state="record_trigger",
                      leave=self.do_nothing),
            Transform(trigger=self.is_known_task, next_state="task", leave=self.do_nothing),
            Transform(trigger=lambda e: not self.is_known_task(e), next_state="new_task",
                      leave=self.from_init_to_new_task)
        ]

    def from_init_to_new_task(self, event):
        self.world["current_query"] = event

    def is_known_task(self, event):
        """
        currently use exact match to find a task
        """
        is_known = False
        actions = os.listdir("./data")
        actions = [f for f in actions if f.endswith(".json")]
        for action_file in actions:
            task = read_json("./data/{}".format(action_file))
            for sent in task["trigger"]:
                if sent == event.query:
                    self.world["task"] = task
                    self.world["task_event"] = event
                    is_known = True
                    break
            if is_known:
                break
        return is_known

    """
    record
    """

    def set_if_not_exist(self, name, default):
        if name not in self.world:
            self.world[name] = default

    def enter_record_trigger(self):
        self.set_if_not_exist("records", [])
        if len(self.world["records"]) != 0:
            self.response = Response("请提供另一个描述/条件不一样的触发语句")
        else:
            self.response = Response("请简要描述一下你要执行的任务，这将作为这个任务的触发语句。")

        self.transform = [
            Transform(trigger=lambda e: True, next_state="record_actions",
                      leave=self.cb_record_trigger)
        ]

    def cb_record_trigger(self, event):
        self.world["records"].append({})
        self.world["records"][-1]["trigger"] = event.query

    def record_next_demo(self, event):
        return len(self.world["records"]) == 1

    def enter_record_actions(self):
        if len(self.world["records"]) == 2:
            self.response = Response("请再次录制执行该触发语句的过程。")
        else:
            self.response = Response("接下来请在右侧模拟器录制你执行任务的过程，启动模拟器后点击播放键开始录制。")
        self.transform = [
            Transform(trigger=self.record_next_demo, next_state="record_trigger",
                      leave=self.cb_record_actions),
            Transform(trigger=lambda e: e.query == "actions", next_state="record_name",
                      leave=self.cb_record_actions)
        ]

    def cb_record_actions(self, event):
        self.world["records"][-1]["actions"] = event.data

    def enter_record_name(self):
        self.response = Response("最后，请为这个任务命名。")
        self.transform = [
            Transform(trigger=lambda e: True, next_state="record", leave=self.cb_record_name)
        ]

    def cb_record_name(self, event):
        self.world["record_task_name"] = event.query

    def enter_record(self):
        # save new tasks
        task = {
            "name": self.world["record_task_name"],
            "records": self.world["records"]
        }
        prev_actions = os.listdir("./data")
        prev_actions = [f for f in prev_actions if f.endswith(".json")]
        task_id = len(prev_actions)
        task["id"] = task_id
        write_json("./data/{}.json".format(task_id), task)

        self.response = Response("已成功记录新任务！")
        self.transform = [
            Transform(trigger=lambda e: True, next_state="init", leave=self.before_init)
        ]

    """
    new task
    """

    def enter_new_task(self):
        self.response = Response("该任务尚未记录，输入绑定来将这个请求绑定到已知任务，输入录制来创建一个新的任务。")
        self.transform = [
            Transform(trigger=lambda e: e.query == "录制", next_state="record_trigger",
                      leave=self.do_nothing),
            Transform(trigger=lambda e: e.query == "绑定", next_state="bind_task",
                      leave=self.do_nothing)
        ]

    def enter_bind_task(self):
        self.response = Response("请输入需要绑定的任务名字：")
        self.transform = [
            Transform(trigger=self.find_task_by_name, next_state="bind", leave=self.do_nothing),
            Transform(trigger=lambda e: not self.find_task_by_name(e), next_state="task_not_found",
                      leave=self.do_nothing)
        ]
        if "before_bind_task" in self.world:
            query = self.world["before_bind_task"]
            del self.world["before_bind_task"]
            self(query)

    def find_task_by_name(self, event):
        """
        currently use exact match to find a task
        """
        is_known = False
        actions = os.listdir("./data")
        actions = [f for f in actions if f.endswith(".json")]
        for action_file in actions:
            task = read_json("./data/{}".format(action_file))
            if event.query == task["name"]:
                is_known = True
                self.world["task_to_bind"] = (action_file, task)
                break
        return is_known

    def enter_bind(self):
        task = self.world["task_to_bind"][1]
        task["trigger"].append(self.world["current_query"].query)
        write_json("./data/{}".format(self.world["task_to_bind"][0]), task)

        self.response = Response(
            "已绑定“{}”到任务：{}".format(self.world["current_query"].query, task["name"]))
        self.transform = [
            Transform(trigger=lambda e: True, next_state="init", leave=self.before_init)
        ]

    def enter_task_not_found(self):
        self.response = Response("未找到对应的任务，请重新输入一个已经创建的任务名字，输入录制则开始创建新任务")
        self.transform = [
            Transform(trigger=lambda e: e.query == "录制", next_state="record_trigger",
                      leave=self.do_nothing),
            Transform(trigger=lambda e: True, next_state="bind_task", leave=self.before_bind_task)
        ]

    def before_bind_task(self, event):
        self.world["before_bind_task"] = event.query

    """
    task
    """

    def action_parser(self, query, task):
        """
        generate actions according to the query and previous demonstration
        """
        return task[0]["actions"]

    def task_has_done(self, event):
        """
        check whether the task is finished
        """
        return self.world["next_action_index"] == len(self.world["current_actions"])

    def task_done(self, event):
        """
        callback function when leaves the state task, delete the "task_done" attribute
        """
        del self.world["executing_task"]

    def save_screen(self, event):
        """
        callback function for re-entering the state task (requiring next action)
        save the current screen data to the world (for deciding next action)
        """
        self.world["current_screen"] = event.data

    def get_next_action(self):
        """
        generate next action according to the current screen
        """
        write_json("./trace/{}.json".format(self.world["next_action_index"]),
                   self.world["current_screen"])
        action = {
            "id": self.world["next_action_index"],
            "action": self.world["current_actions"][self.world["next_action_index"]]
        }
        self.world["next_action_index"] += 1
        return action

    def enter_task(self):
        """
        it will be two situation:
        1. The first time enter the state task: initialize the actions and save them in world, set
            the trigger and response.
        2. The 2+ time enter the state task: get the next action and return
        """
        if "executing_task" in self.world:
            action = self.get_next_action()
            self.response = Response("action", actions=[action])
            return
        task = self.world["task"]
        query = self.world["task_event"].query
        actions = self.action_parser(query, task)
        self.world["current_actions"] = actions
        self.world["next_action_index"] = 0
        self.world["executing_task"] = True

        self.response = Response("匹配到任务：{}， 正在执行".format(task["name"]), True)
        self.transform = [
            Transform(trigger=lambda e: not self.task_has_done(e), next_state="task",
                      leave=self.save_screen),
            Transform(trigger=lambda e: self.task_has_done, next_state="init", leave=self.task_done)
        ]


if __name__ == "__main__":
    pipeline = Pipeline()
    """
    >> 录制
    请简要描述一下你要执行的任务，这将作为这个任务的触发语句。
    >> 测试任务
    接下来请在右侧模拟器录制你执行任务的过程，启动模拟器后点击播放键开始录制。
    >> actions
    最后，请为这个任务命名。
    >> 测试
    已成功记录新任务！
    >> 测试
    >> 测试
    你好，输入录制开始录制新任务，或者直接输入需要执行的任务。
    """
    # pipeline("录制")
    # print(pipeline)
    # pipeline("测试任务")
    # print(pipeline)
    # pipeline("actions", [0])
    # print(pipeline)
    # pipeline("测试任务")
    # print(pipeline)
    # pipeline("actions")
    # print(pipeline)
    # pipeline("测试任务")
    # print(pipeline)

    """
    >> 点外卖
    该任务尚未记录，输入绑定来将这个请求绑定到已知任务，输入录制来创建一个新的任务。
    >> 录制
    ...
    """
    pipeline("点外卖")
    print(pipeline.response.res)
    pipeline("录制")
    print(pipeline.response.res)
    """
    >> 帮我点外卖
    该任务尚未记录，输入绑定来将这个请求绑定到已知任务，输入录制来创建一个新的任务。
    >> 绑定
    请输入需要绑定的任务名字：
    >> 点外卖
    已绑定“帮我点外卖”到任务：点外卖
    """
    # pipeline("点外卖")
    # print(pipeline.response.res)
    # pipeline("绑定")
    # print(pipeline.response.res)
    # pipeline("测试")
    # print(pipeline.response.res)
    """
    >> 帮我点外卖
    该任务尚未记录，输入绑定来将这个请求绑定到已知任务，输入录制来创建一个新的任务。
    >> 绑定
    请输入需要绑定的任务名字
    >> 点外卖8
    未找到任务：点外卖8，请重新输入一个已经创建的任务名字，输入录制则开始创建新任务
    """
    # pipeline("帮我点外卖")
    # print(pipeline.response.res)
    # pipeline("绑定")
    # print(pipeline.response.res)
    # pipeline("测试3")
    # print(pipeline.response.res)
    # pipeline("测试")
    # print(pipeline.response.res)
    """
    >> 帮我点外卖
    匹配到任务：点外卖，正在执行
    >> 绑定
    请输入需要绑定的任务名字
    >> 点外卖8
    未找到任务：点外卖8，请重新输入一个已经创建的任务名字，输入录制则开始创建新任务
    """
    # pipeline("我要点外卖")
    # print(pipeline.response.res)
    # pipeline("task finish")
    # print(pipeline.response.res)
    """
    >> 测试
    
    """
    # pipeline("测试")
    # print(pipeline.response.res)
    # pipeline("get_action")
    # print(pipeline.response.res)
    # print(pipeline.response.actions)
