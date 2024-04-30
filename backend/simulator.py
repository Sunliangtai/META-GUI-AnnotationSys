import base64
from action import Action, parse_img, perform, parse_layout
from utils import image_to_base64, read_json, write_json, write_file
import os
import threading
import json
from PIL import Image, ImageDraw
import xml.dom.minidom as xdm
import shutil
import xlrd
import random
import time


def shrink(img, ratio):
    return img.resize([int(img.size[0] * ratio), int(img.size[1] * ratio)])


def parse_action(action_str):
    if action_str is None:
        return {"action": "无"}
    if "scroll" in action_str:
        # test|scroll|720,853|720,1706
        start = action_str.split("|")[2]
        end = action_str.split("|")[3]
        x1, y1 = int(start.split(",")[0]), int(start.split(",")[1])
        x2, y2 = int(end.split(",")[0]), int(end.split(",")[1])
        if x1 == x2:
            if y1 < y2:
                action_type = "下滑"
            else:
                action_type = "上滑"
        elif y1 == y2:
            if x1 < x2:
                action_type = "右滑"
            else:
                action_type = "左滑"
        else:
            action_type = "滑动"
        return {"action": action_type}

    elif "click" in action_str:
        # test|click|1276,2252|NULL
        pos = action_str.split("|")[2]
        x, y = pos.split(",")
        x = int(x)
        y = int(y)
        return {"action": "点击", "x1": x, "y1": y, "text": "点击位置：{},{}".format(x, y)}
    elif "typing" in action_str:
        # test|typing|NULL|surgery
        text = action_str.split("|")[-1]
        return {"action": "输入", "text": text}
    elif "read" in action_str:
        # test|read|NULL|NULL
        top, left, height, width = action_str.split("|")[-1].split(",")
        top, left, height, width = int(top), int(left), int(height), int(width)
        return {"action": "读取", "top": top, "left": left, "height": height, "width": width}

    elif "back" in action_str:
        # test|back|NULL|NULL
        return {"action": "返回"}
    elif "clear" in action_str:
        # test|clear|NULL|NULL
        return {"action": "清除输入"}
    elif "enter" in action_str:
        # test|enter|NULL|NULL
        return {"action": "回车"}
    elif "home" in action_str:
        return {"action": "home"}


class MyThread(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    def result(self):
        return self.res


class Manager:
    def __init__(self):
        self.current_dialog = None
        self.screenshot_record = {}
        self.layout_record = {}
        self.screenshot_id = 0
        self.current_turn = 0
        self.action_record = {}
        self.last_action = None
        with open("./data/dialog_data/SMCalFlow_extracted_data.json", 'r', encoding="utf8") as f:
            self.data = json.load(f)
        self.data_index = {}
        for i, data in enumerate(self.data):
            self.data_index[data["id"]] = i
        self.annotated_data = []
        self.get_annotated_data()
        if not os.path.exists("./data/user_test"):
            os.mkdir("./data/user_test")
        workbook = xlrd.open_workbook("加州餐厅数据.xls")
        sheet = workbook.sheet_by_index(0)
        rows = sheet.nrows
        self.place = []
        for row in range(1, rows):
            self.place.append(sheet.row_values(row))

    def reset(self, uid):
        """
        user reflash page, reset all record
        """
        self.screenshot_record = {}
        self.layout_record = {}
        self.screenshot_id = 0
        self.current_turn = 0
        self.action_record = {}
        self.last_action = None

    def endDialog(self, uid):
        self.reset(uid)

    def get_annotated_data(self):
        path = "./data/annotated_data.json"
        if os.path.exists(path):
            with open(path, 'r') as reader:
                self.annotated_data = json.load(reader)

    def save_annotated_data(self):
        path = "./data/annotated_data.json"
        with open(path, 'w') as writer:
            json.dump(self.annotated_data, writer)

    def save(self, uid, screen_list, dialog, turn_id, goals, lan_infos):
        """
        user click save button
        params:
            screen_list: the list of screen ids
        """
        if self.current_dialog not in self.annotated_data:
            self.annotated_data.append(self.current_dialog)
            self.save_annotated_data()
        user_path = f"./data/user_{uid}"
        if not os.path.exists(user_path):
            os.mkdir(user_path)
        main_path = os.path.join(user_path, f"trace_{self.data_index[self.current_dialog]}")
        if not os.path.exists(main_path):
            os.mkdir(main_path)
        save_path = os.path.join(
            main_path, "turn_{}".format(turn_id))
        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        os.mkdir(save_path)
        write_json(os.path.join(main_path, "dialogue.json"), dialog)
        write_file(os.path.join(main_path, "dialogue_id.txt"),
                   self.current_dialog)
        actions = {}
        print(screen_list)
        for i, screen_id in enumerate(screen_list):
            print(f"{i} {screen_id}")
            img = self.screenshot_record[screen_id]
            layout = self.layout_record[screen_id]
            write_file(os.path.join(save_path, "%d.xml" % i), layout)
            img.save(os.path.join(save_path, "%d.png" % i))
            if i != 0:
                actions[i - 1] = self.action_record[screen_id]
        write_json(os.path.join(save_path, "actions.json"), actions)

        save_goals = {
            "goals": goals,
            "lan_infos": lan_infos,
        }
        goals_path = os.path.join(main_path, "goals.json")
        write_json(goals_path, save_goals)

    def get_img_layout_multi(self, uid):

        img_thread = MyThread(parse_img, (uid,))
        layout_thread = MyThread(parse_layout, (uid,))
        img_thread.start()
        layout_thread.start()
        img_thread.join()
        layout_thread.join()
        img = img_thread.result()
        layout = layout_thread.result()
        """img = parse_img(uid)
        layout = parse_layout(uid)
        """
        return img, layout

    def get_screenshot(self, uid):
        """
        get screenshot and ui
        Returns:
            screenshot: base64 encoding
            screen_id: int or str
        """
        print("get screenshot")
        img, layout = self.get_img_layout_multi(uid)
        self.screenshot_id = self.screenshot_id + 1
        self.screenshot_record[self.screenshot_id] = img
        self.layout_record[self.screenshot_id] = layout
        print(img.size)
        img = shrink(img, 0.25)
        self.action_record[self.screenshot_id] = self.last_action
        print("get screenshot {}".format(self.screenshot_id))
        return image_to_base64(img), self.screenshot_id

    def do_action(self, uid, action):
        """
        user perform an action
        """
        act = None
        if action["type"] == "click":
            act = Action("click", action["x"], action["y"])
            self.last_click = act
        if action["type"] == "swipe":
            act = Action("scroll",
                         action["x1"], action["y1"],
                         "{},{}".format(action["x2"], action["y2"]))
        if action["type"] == "input":
            act = Action("typing",
                         text=action["text"])
        if action["type"] == "back":
            act = Action("back")
        if action["type"] == "clear":
            act = Action("clear")
        if action["type"] == "read":
            # test|read|NULL|top,left,height,width
            act = Action("read", text="{},{},{},{}".format(
                action["top"], action["left"], action["height"], action["width"]
            ))
        if action["type"] == "enter":
            act = Action("enter")
        if action["type"] == "home":
            act = Action("home")
        action_string = act.parse(uid)
        print("do action:", action_string)
        self.last_action = action_string
        perform(action_string)
        return 1

    def init_record(self, uid):
        """
        user click start record button
        """
        print("init record")

    def end_record(self, uid, dialog_id):
        """
        user click end record button
        """
        print("end record")

    def get_review_dialog(self, uid):
        trace_folders = os.listdir("./data/user_{}".format(uid))
        dialog_id = []
        for trace_folder in trace_folders:
            dialogue_id_path = "./data/user_{}/{}/dialogue_id.txt".format(
                uid, trace_folder)
            check_status_path = "./data/user_{}/{}/check_status.txt".format(uid, trace_folder)
            if os.path.exists(check_status_path):
                with open(check_status_path, "r") as f:
                    check_status = int(f.read().strip())
            else:
                check_status = -1
            if os.path.exists(dialogue_id_path):
                with open(dialogue_id_path, "r") as f:
                    did = f.read().strip()
                    if did:
                        full_dialog = read_json(
                            "./data/user_{}/{}/dialogue.json".format(uid, trace_folder))

                        dialog_id.append(
                            {"dialog_id": did, "dialog": full_dialog, "name": trace_folder,
                             "check_status": check_status})

        return dialog_id

    def check_trace(self, uid, dialogue_id, turn_id):
        trace_folder = f"trace_{self.data_index[dialogue_id]}"
        check_status_file = "./data/user_{}/{}/check_status.txt".format(uid, trace_folder)
        if os.path.exists(check_status_file):
            with open(check_status_file, 'r') as reader:
                check_status = int(reader.read().strip())
        else:
            check_status = -1
        raw_img = []
        pil_img = []
        return_img = []
        layout_record = []
        actions = []
        turn_folder = "./data/user_{}/{}/turn_{}".format(
            uid, trace_folder, turn_id)
        if os.path.exists(turn_folder) and len(os.listdir(turn_folder)) != 0:
            num_steps = len(os.listdir(turn_folder)) // 2
            for step in range(num_steps):

                image = Image.open(os.path.join(
                    turn_folder, "{}.png".format(step)), 'r')

                dom = xdm.parse(os.path.join(
                    turn_folder, "{}.xml".format(step)))

                layout_record.append(dom.toxml())
                border = []
                raw_img.append("data:image/png;base64," +
                               image_to_base64(shrink(image, 0.25)).decode("utf8"))
                pil_img.append(image.copy())

                def dfs(tree):
                    if tree.attributes:
                        clickable = tree.attributes.getNamedItem(
                            'clickable')
                        enabled = tree.attributes.getNamedItem('enabled')
                        if clickable and enabled and enabled.nodeValue == 'true':  # and clickable.nodeValue == 'true':
                            attributes = tree.attributes.getNamedItem(
                                'bounds')
                            if attributes:
                                bounds = attributes.nodeValue
                                left_top, right_bottom, _ = bounds.split(']')
                                left_top = left_top[1:]
                                right_bottom = right_bottom[1:]
                                left, top = map(int, left_top.split(','))
                                right, bottom = map(
                                    int, right_bottom.split(','))
                                border.append((left, top, right, bottom))

                    for child in tree.childNodes:
                        dfs(child)

                def draw(img, borders):
                    for bd in borders:
                        left, top, right, bottom = bd
                        if left == right or top == bottom or left == right - 1 or top == bottom - 1:
                            continue
                        shape = [(left, top), (right, bottom)]
                        img1 = ImageDraw.Draw(img)
                        img1.rectangle(shape, outline="red", width=3)

                    return img

                dfs(dom)
                image = draw(image, border)
                return_img.append(
                    "data:image/png;base64," + image_to_base64(shrink(image, 0.25)).decode("utf8"))

            action_json = os.path.join(turn_folder, "actions.json")
            with open(action_json, "r") as reader:
                actions = json.loads(reader.read())
            for i in range(len(raw_img)):
                self.screenshot_id += 1
                self.screenshot_record[self.screenshot_id] = pil_img[i]
                self.layout_record[self.screenshot_id] = layout_record[i]
                if i != 0:
                    self.action_record[self.screenshot_id] = actions[f"{i - 1}"]
                raw_img[i] = (raw_img[i], self.screenshot_id)
                return_img[i] = (return_img[i], self.screenshot_id)
            actions = [parse_action(actions[a]) for a in actions]

        goals_path = f"./data/user_{uid}/{trace_folder}/goals.json"
        if os.path.exists(goals_path):
            with open(goals_path, 'r', encoding="utf-8") as reader:
                goals = json.load(reader)

            return raw_img, return_img, actions, check_status, goals["goals"], goals["lan_infos"]
        else:
            goals, lan_infos = self.generate_goals()
            return raw_img, return_img, actions, check_status, goals, lan_infos

    def check_save(self, uid, trace_id, turn_id, screen_list, dialog, check_status):
        save_path = "./data/user_{}/{}/review".format(uid, trace_id)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        turn_save_path = os.path.join(save_path, "turn_{}".format(turn_id))
        if os.path.exists(turn_save_path):
            shutil.rmtree(turn_save_path)
        os.mkdir(turn_save_path)
        write_json(os.path.join(save_path, "dialogue.json"), dialog)
        actions = {}
        write_file("./data/user_{}/{}/check_status.txt".format(uid, trace_id), str(check_status))
        for i, screen_id in enumerate(screen_list):
            img = self.screenshot_record[screen_id]
            layout = self.layout_record[screen_id]
            write_file(os.path.join(turn_save_path, "%d.xml" % i), layout)
            img.save(os.path.join(turn_save_path, "%d.png" % i))
            if i != 0:
                actions[i - 1] = self.action_record[screen_id]
        write_json(os.path.join(turn_save_path, "actions.json"), actions)

    def get_dialogue(self, dialogue_id):
        saved_path = f"./data/user_test/trace_{self.data_index[dialogue_id]}/dialogue.json"
        if os.path.exists(saved_path):
            with open(saved_path, 'r') as reader:
                dialogue = json.load(reader)
            return_data = {"id": dialogue_id,
                           "turns": dialogue,
                           "status": 1}
            return return_data
        else:
            chosen_data = None
            for data in self.data:
                if data["id"] == dialogue_id:
                    chosen_data = data
                    break
            if chosen_data is None:
                return {
                    "status": 0,
                }
            return_data = {"id": chosen_data["id"]}
            turns = []
            chosen_turns = chosen_data["turns"]

            for turn in chosen_turns:
                try:
                    turns.append({
                        "isUser": turn["isUser"],
                        "text": turn['utterance'],
                        "program": turn['program']
                    })
                except KeyError:
                    turns.append({
                        "isUser": turn["isUser"],
                        "text": turn['text'],
                        "program": turn['program']
                    })
            # length_turn = len(turns)
            # chosen_turn = random.randint(1, length_turn)
            return_data["turns"] = turns  # [:2 * chosen_turn]
            return_data["status"] = 1

            return return_data

    def get_all_dialogue(self, uid):
        dialogues = []
        for data in self.data:
            dialogue_id = data["id"]
            dialogue = self.get_dialogue(dialogue_id)
            all_turns = len(dialogue["turns"]) // 2
            folder = f"./data/user_{uid}/trace_{self.data_index[dialogue_id]}/"
            if os.path.exists(folder):
                all_turn_folder = os.listdir(folder)
                annotated_turns = len([folder for folder in all_turn_folder if folder.startswith("turn")])
            else:
                annotated_turns = 0
            dialogues.append(
                {"dialog_id": dialogue_id, "name": f"trace_{self.data_index[dialogue_id]}",
                 "annotated_turns": annotated_turns, "all_turns": all_turns})

        return dialogues

    def generate_goals(self):
        lan_phys = ["无", "修改", "添加"]

        def hotel():
            while True:
                hotel_place = random.sample(self.place, k=1)[0]
                if hotel_place[3] == "酒店":
                    continue
                else:
                    break

            checkins = [i for i in range(16)]
            checkin = random.sample(checkins, k=1)[0]

            days = [1, 2, 3, 4, 5, 6, 7, 8]
            days_weight = [1, 1, 1, 0.25, 0.11, 0.06, 0.04, 0.03]
            day = random.choices(days, weights=days_weight, k=1)[0]

            rooms = [1, 2, 3, 4]
            rooms_weight = [1, 1 / 2 / 2, 1 / 3 / 3, 1 / 4 / 4]
            room = random.choices(rooms, weights=rooms_weight, k=1)[0]

            adult = room
            person_number = room
            persons = [i for i in range(person_number + 1)]
            adult = adult + random.sample(persons, k=1)[0]
            children = [i for i in range(2 * room - adult + 1)]
            child = random.sample(children, k=1)[0]

            budgets = ["0$-58$", "58$-116$", "116$-174$", "174$-232$", "232$+"]
            budget_weight = [4, 9, 16, 9, 3]
            budget = random.choices(budgets, weights=budget_weight, k=1)[0]

            use_free_cancel = True if random.randint(1, 100) < 10 else False

            use_health_and_safety = True if random.randint(1, 100) < 5 else False

            use_genius_discount = True if random.randint(1, 100) < 5 else False

            use_stars = True if random.randint(1, 100) < 20 else False
            stars = ["unrated", "1 start/other ratings", "2 stars/other ratings", "3 stars/other ratings",
                     "4 stars/other ratings",
                     "5 stars/other ratings"]
            stars_weight = [176, 21, 340, 420, 145, 30]
            star = random.choices(stars, weights=stars_weight, k=1)[0]

            use_property_type = True if random.randint(1, 100) < 10 else False
            property_types = ["Hotels", "Motels", "Apartments", "Hostels", "Vacation Homes", "Homestays", "Resorts",
                              "Bed and Breakfasts", "Villas", "Guesthouses", "Luxury tents"]
            property_types_weight = [722, 260, 74, 26, 15, 12, 11, 8, 6, 5, 1]
            property_type = random.choices(property_types, weights=property_types_weight, k=1)[0]

            facilities = ["airport shuttle", "airport shuttle (free)", "BBQ facilities",
                          "electric vehicle charging station",
                          "facilities for disabled guests", "family rooms", "fitness center", "free parking",
                          "free WIFI",
                          "non-smoking rooms", "parking", "pet friendly", "restaurant", "room service", "spa",
                          "swimming pool"]
            facilities_weight = [58, 34, 68, 139, 679, 588, 380, 619, 859, 1005, 1006, 339, 289, 261, 55, 466]
            facilities_nums = [1, 2, 3, 4, 5]
            facilities_nums_weight = [9, 25, 9, 4, 1]
            facilities_num = random.choices(facilities_nums, weights=facilities_nums_weight, k=1)[0]
            facility = random.choices(facilities, weights=facilities_weight, k=facilities_num)

            use_distance_from_address = True if random.randint(1, 100) < 5 else False
            distances_from_address = ["Less than 1/2 miles", "Less than 1 mile", "Less than 2 miles"]
            distances_from_address_weight = [1, 9, 25]
            distance_from_address = random.choices(distances_from_address, weights=distances_from_address_weight, k=1)[
                0]

            use_meals = True if random.randint(1, 100) < 5 else False
            meals = ["Breakfast included", "All-inclusive", "Kitchen facilities"]
            meals_weight = [81, 1, 9]
            meal = random.choices(meals, weights=meals_weight, k=1)[0]

            use_chain = True if random.randint(1, 100) < 15 else False
            chains = ["Best Western", "Best Western Plus", "Comfort Inn", "Courtyard by Marriott", "Days Inn",
                      "Doubletree by Hilton", "Embassy Suites Hotels", "Extended Stay America", "Fairfield Inn",
                      "Hampton by Hilton", "Hilton Garden Inn", "Hilton Hotels & Resorts", "Holiday Inn Express",
                      "Holiday Inn Hotels & Resorts", "Marriott Hotels & Resorts", "Motel6", "Quality Inn", "Ramada",
                      "Residence Inn", "Rodeway Inn", "Sheraton", "Sonesta Hotels", "SpringHill Suites", "Super 8",
                      "Travelodge by Wyndham"]
            chains_weight = [20, 23, 8, 21, 16, 15, 9, 21, 6, 18, 10, 12, 13, 10, 10, 32, 16, 12, 15, 9, 8, 9, 6, 10,
                             15]
            chain = random.choices(chains, weights=chains_weight, k=1)[0]

            use_review_scores = True if random.randint(1, 100) < 15 else False
            review_scores = ["Fair 5+", "Pleasant 6+", "Good 7+", "Very Good 8+", "Wonderful 9+", "No rating"]
            review_scores_weight = [36, 25, 16, 9, 4, 4]
            review_score = random.choices(review_scores, weights=review_scores_weight, k=1)[0]

            room_facilities = ["Private bathroom", "Air conditioning", "Flag-screen TV", "Balcony", "Bathtub",
                               "Spa tub",
                               "Coffee/Tea maker", "Kitchen/Kitchenette", "Ocean view", "View", "Terrace",
                               "Washing machine",
                               "Private pool", "Patio", "Soundproof", "Electric kettle", "Coffee machine"]
            room_facilities_weight = [953, 1049, 860, 189, 540, 70, 586, 210, 31, 249, 64, 87, 25, 94, 87, 74, 339]
            room_facilities_nums = [1, 2, 3, 4, 5]
            room_facilities_nums_weight = [25, 16, 9, 4, 1]
            room_facilities_num = random.choices(room_facilities_nums, weights=room_facilities_nums_weight, k=1)[0]
            room_facility = random.choices(room_facilities, weights=room_facilities_weight, k=room_facilities_num)[0]

            use_bed_preference = True if random.randint(1, 100) < 10 else False
            bed_preferences = ["2 single beds", "Double bed"]
            bed_preference_weight = [1, 9]
            bed_preference = random.choices(bed_preferences, weights=bed_preference_weight, k=1)[0]

            chosen = ["nearest", "most popular", "highest review score", "highest rating", "lowest rating", "cheapest"]
            choice = random.choices(chosen, k=1)[0]

            lan_phy = random.sample(lan_phys, k=1)[0]
            if lan_phy == "无":
                lan_info = "无"
            elif lan_phy == "修改":
                changes = ["hotel_place", "checkin", "day", "room", "budget"]
                change = random.sample(changes, k=1)[0]
                if change == "hotel_place":
                    while True:
                        hotel_place_change = random.sample(self.place, k=1)[0]
                        if hotel_place_change[3] == "酒店" or hotel_place_change[6] == hotel_place[6]:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要在{hotel_place_change[7] if hotel_place_change[7] != '' else hotel_place_change[6]}定酒店"
                elif change == "checkin":
                    while True:
                        checkin_change = random.sample(checkins, k=1)[0]
                        if checkin_change == checkin:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要在{checkin_change}天后入住"
                elif change == "day":
                    while True:
                        day_change = random.choices(days, weights=days_weight, k=1)[0]
                        if day_change == day:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要住{day_change}晚"
                elif change == "room":
                    while True:
                        room_change = random.choices(rooms, weights=rooms_weight, k=1)[0]
                        if room_change == room:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要订{room_change}间房间"
                elif change == "budget":
                    while True:
                        budget_change = random.choices(budgets, weights=budget_weight, k=1)[0]
                        if budget_change == budget:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本的预算为{budget_change}每天"
            elif lan_phy == "添加":
                candidates = []
                choices = {
                    "Free cancellation": use_free_cancel,
                    "Properties that take health & safety measures": use_health_and_safety,
                    "Genius benefits": use_genius_discount,
                    "Stars and other ratings": use_stars,
                    "Property type": use_property_type,
                    "Distance from address": use_distance_from_address,
                    "Meals": use_meals,
                    "Chain": use_chain,
                    "Review Score": use_review_scores,
                    "Bed Preference": use_bed_preference,
                }
                for key, value in choices.items():
                    if value:
                        candidates.append(key)
                if type(facility) == list:
                    candidates += facility
                else:
                    candidates.append(facility)
                if type(room_facility) == list:
                    candidates += room_facility
                else:
                    candidates.append(room_facility)
                lan_change = random.sample(candidates, k=1)[0]
                lan_info = f"添加: 你原本没有想要限制{lan_change}"

            return f"Goals: 你要在 {hotel_place[7] if hotel_place[7] != '' else hotel_place[6]} 定酒店，入住时间为{checkin}天后，" \
                   f"共{day}晚，房间数为{room}，成人数量为{adult}，儿童数量为{child}，预算为{budget}每天，\n " \
                   f"Free cancellation: {'是' if use_free_cancel else '否'}，\n" \
                   f"Properties that take health & safety measures: {'是' if use_health_and_safety else '否'}，\n" \
                   f"Genius benefits: {'是' if use_genius_discount else '否'}，\n" \
                   f"Stars and other ratings: {star if use_stars else '否'}，\n" \
                   f"Property type: {property_type if use_property_type else '否'}，\n" \
                   f"Facilities: {facility}，\n" \
                   f"Distance from address: {distance_from_address if use_distance_from_address else '否'}，\n" \
                   f"Meals: {meal if use_meals else '否'}，\n" \
                   f"Chain: {chain if use_chain else '否'}，\n" \
                   f"Review Score: {review_score if use_review_scores else '否'}，\n" \
                   f"Room Facilities: {room_facility}，\n" \
                   f"Bed Preference: {bed_preference if use_bed_preference else '否'}, \n" \
                   f"Choice: {choice}", lan_info

        all_time = []
        for i in range(8, 21):
            for j in ["00", "15", "30", "45"]:
                all_time.append(f"{i}:" + j)
        all_time.append("current time")

        def compare_time(time1, time2):
            hour1, min1 = map(int, time1.split(":"))
            hour2, min2 = map(int, time2.split(":"))
            if hour1 > hour2:
                return True
            elif hour1 < hour2:
                return False
            elif min1 > min2:
                return True
            else:
                return False

        def taxi():
            start, end = random.sample(self.place, k=2)
            time_struct = time.localtime()

            current_time = f"{time_struct.tm_hour}:{time_struct.tm_min}"
            all_time_weight = []
            all_time_cnt = 1
            for t in range(len(all_time) - 1):
                if compare_time(all_time[t], current_time):
                    all_time_weight.append(1 / all_time_cnt)
                    all_time_cnt += 1
                else:
                    all_time_weight.append(0)

            all_time_weight.append(2 * sum(all_time_weight))
            time_chosen = random.choices(all_time, weights=all_time_weight, k=1)[0]

            lan_phys_weight = [1, 1, 0]
            lan_phy = random.choices(lan_phys, weights=lan_phys_weight, k=1)[0]
            if lan_phy == "无":
                lan_info = "无"
            elif lan_phy == "修改":
                changes = ["start", "end", "time_chosen"]
                change = random.sample(changes, k=1)[0]
                if change == "start":
                    while True:
                        start_change = random.sample(self.place, k=1)[0]
                        if start_change == start or start_change == end:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要打车从{start_change[7] if start_change[7] != '' else start_change[6]}出发"
                elif change == "end":
                    while True:
                        end_change = random.sample(self.place, k=1)[0]
                        if end_change == start or end_change == end:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要打车去{end_change[7] if end_change[7] != '' else end_change[6]}"
                elif change == "time_chosen":
                    while True:
                        time_chosen_change = random.choices(all_time, weights=all_time_weight, k=1)[0]
                        if time_chosen_change == time_chosen:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本的出发时间为{time_chosen_change}"

            return f"Goals: 你要打车从{start[7] if start[7] != '' else start[6]}出发，到{end[7] if end[7] != '' else end[6]}去，" \
                   f"出发时间为{time_chosen}，车型或者价格区间请根据实际情况进行选择", lan_info

        def restaurant():
            while True:
                res_place = random.sample(self.place, k=1)[0]
                if res_place[3] == "美食":
                    continue
                else:
                    break
            food_types = ["pizza", "burgers", "tacos", "sandwiches", "salad", "Italian", "Mexican", "Chinese", "Korean",
                          "Noodles", "dumplings", "fast food", "comfort food", "fried chicken", "french fries", "soup",
                          "pasta"]
            food_type = random.sample(food_types, k=1)[0]

            use_price = True if random.randint(1, 100) < 30 else False
            prices = ["$", "$$", "$$$", "$$$$"]
            price = random.sample(prices, k=1)[0]

            use_distance = True if random.randint(1, 100) < 10 else False
            distances = ["2 blocks", "6 blocks", "1 mile", "5 miles"]
            distance = random.sample(distances, k=1)[0]

            use_sort = True if random.randint(1, 100) < 10 else False
            sorts = ["recommended", "distance", "rating", "most reviewed"]
            sorts_weight = [16, 9, 9, 1]
            sort = random.choices(sorts, weights=sorts_weight, k=1)[0]

            use_service = True if random.randint(1, 100) < 10 else False
            services = ["yelp delivery", "yelp takeout", "reservations"]
            service = random.sample(services, k=1)[0]

            times = ["breakfast", "brunch", "lunch", "dinner", "dessert", "late night"]
            time_ = random.sample(times, k=1)[0]

            amenities = ["free WIFI", "dogs allowed", "gender-neutral restrooms", "wheelchair accessible",
                         "offers delivery",
                         "offers takeout", "takes reservations", "outdoor seating", "full bar",
                         "proof of vaccination required",
                         "all staff fully vaccinated"]
            amenities_weight = [16, 2, 4, 2, 8, 8, 8, 8, 2, 2, 2]

            num_amenities = [1, 2, 3]
            num_amenities_weight = [60, 30, 10]
            num_amenity = random.choices(num_amenities, weights=num_amenities_weight, k=1)[0]
            amenity = random.choices(amenities, weights=amenities_weight, k=num_amenity)

            lan_phy = random.sample(lan_phys, k=1)[0]
            if lan_phy == "无":
                lan_info = "无"
            elif lan_phy == "修改":
                changes = ["res_place", "food_type"]
                change = random.sample(changes, k=1)[0]
                if change == "res_place":
                    while True:
                        res_place_change = random.sample(self.place, k=1)[0]
                        if res_place_change[3] == "美食" or res_place_change == res_place:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要在{res_place_change[7] if res_place_change[7] != '' else res_place_change[6]}吃饭"
                elif change == "food_type":
                    while True:
                        food_type_change = random.sample(food_types, k=1)[0]
                        if food_type_change == food_type:
                            continue
                        else:
                            break
                    lan_info = f"修改: 你原本想要吃的食物类型为{food_type_change}"
            elif lan_phy == "添加":
                candidates = []
                choices = {
                    "Price": use_price,
                    "Distance": use_distance,
                    "Sort by": use_sort,
                    "Offering": use_service,
                }
                for key, value in choices.items():
                    if value:
                        candidates.append(key)
                candidates.append(time_)
                if type(amenity) == list:
                    candidates += amenity
                else:
                    candidates.append(amenity)
                lan_change = random.sample(candidates, k=1)[0]
                lan_info = f"添加: 你原本没有想要限制{lan_change}"
            return f"Goals: 你想要在{res_place[7] if res_place[7] != '' else res_place[6]}吃饭，食物类型为{food_type}， \n" \
                   f"Price: {price if use_price else '否'}, \n" \
                   f"Distance: {distance if use_distance else '否'}, \n" \
                   f"Sort by: {sort if use_sort else '否'}, \n" \
                   f"Offering: {service if use_service else '否'}, \n" \
                   f"Meal: {time_}, \n" \
                   f"Amenities & More: {amenity}", lan_info

        dialog_types = ["hotel", "taxi", "restaurant"]
        dialog_type = random.sample(dialog_types, k=1)[0]
        if dialog_type == "hotel":
            goals, lan_infos = hotel()
        elif dialog_type == "taxi":
            goals, lan_infos = taxi()
        else:
            goals, lan_infos = restaurant()

        return goals, lan_infos

    def add_dialog(self, dialog_id, turn_id):
        trace_id = self.data_index[dialog_id]
        trace_folder = f"./data/user_test/trace_{trace_id}"
        if not os.path.exists(trace_folder):
            os.mkdir(trace_folder)
        folders = os.listdir(trace_folder)
        turn_folder = sorted([f for f in folders if f.startswith("turn")])
        change_turn_folder = []
        for t in turn_folder:
            if int(t.split("_")[-1]) >= int(turn_id):
                change_turn_folder.append(t)

        change_turn_folder = sorted(change_turn_folder, reverse=True)
        for t in change_turn_folder:
            c_turn_id = int(t.split("_")[-1])
            os.rename(os.path.join(trace_folder, f"turn_{c_turn_id}"), os.path.join(trace_folder, f"turn_{c_turn_id+1}"))

        new_turn_path = os.path.join(trace_folder, f"turn_{turn_id}")
        if not os.path.exists(new_turn_path):
            os.mkdir(new_turn_path)

    def delete_dialog(self, dialog_id, turn_id):
        trace_id = self.data_index[dialog_id]
        trace_folder = f"./data/user_test/trace_{trace_id}"
        if not os.path.exists(trace_folder):
            return
        folders = os.listdir(trace_folder)
        turn_folder = sorted([f for f in folders if f.startswith("turn")])
        delete_turn_path = os.path.join(trace_folder, f"turn_{turn_id}")
        if os.path.exists(delete_turn_path):
            shutil.rmtree(delete_turn_path)
        for t in turn_folder:
            c_turn_id = int(t.split("_")[-1])
            if c_turn_id > int(turn_id):
                os.rename(os.path.join(trace_folder, f"turn_{c_turn_id}"), os.path.join(trace_folder, f"turn_{c_turn_id-1}"))
