from flask import Flask, request, send_file
from records import save_actions, get_actions
# from flask_jwt_extended import create_access_token
# from flask_jwt_extended import get_jwt_identity
# from flask_jwt_extended import jwt_required
# from flask_jwt_extended import JWTManager
from pipeline import Pipeline
from simulator import Manager
from flask_compress import Compress
import time
import random
from RenderLispress import render
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ipa'
Compress(app)
pipeline = Pipeline()
manager = Manager()


# jwt = JWTManager(app)

@app.route("/", methods=["GET"])
def main():
    return send_file("./template/index.html")

@app.route("/saveActions", methods=["POST"])
def save_action():
    actions = request.json
    save_actions(actions)
    return {"status": 1}


@app.route("/getActions", methods=["GET"])
def get_action():
    return get_actions(0)


@app.route("/getScreenshot", methods=["GET"])
def get_screenshot():
    begin = time.time()
    query = request.args
    uid = query["uid"]
    screenshot, screen_id = manager.get_screenshot(uid)
    screenshot = "data:image/png;base64," + screenshot.decode("utf8")
    print("get screenshot use", time.time() - begin, "s")
    return {"status": 1, "screenshot": screenshot, "screen_id": screen_id}


@app.route("/startRecord", methods=["POST"])
def init_record():
    uid = request.json["uid"]
    manager.init_record(uid)
    return {"status": 1}


@app.route("/endRecord", methods=["POST"])
def end_record():
    uid = request.json["uid"]
    manager.endDialog(uid)
    return {"status": 1}


@app.route("/save", methods=["POST"])
def save():
    screen_list = request.json["screens"]
    dialog = request.json["dialog"]
    turn_id = request.json["turn"]
    goals = request.json["goals"]
    lan_infos = request.json["lan_infos"]
    print("save", screen_list, dialog, turn_id)
    manager.save("test", screen_list, dialog, turn_id, goals, lan_infos)
    return {"status": 1}


@app.route("/saveReview", methods=["POST"])
def saveReview():
    screen_list = request.json["screens"]
    dialog = request.json["dialog"]
    trace_id = request.json["trace"]
    turn_id = request.json["turn"]
    check_status = request.json["check_status"]
    manager.check_save("test", trace_id, turn_id, screen_list, dialog, check_status)
    return {"status": 1}


@app.route("/doAction", methods=["POST"])
def do_action():
    begin = time.time()
    query = request.json
    uid, action = query["uid"], query["action"]
    status = manager.do_action(uid, action)
    print("do action use", time.time() - begin, "s")
    return {"status": status}


@app.route("/dialog/chat", methods=["POST"])
def chat():
    query = request.json["message"]
    if query == "actions":
        pipeline(query, request.json["data"])
    elif query == "get_action":
        pipeline(query, request.json["data"])
    else:
        pipeline(query)
    response = pipeline.response
    if response.actions is None:
        return {"status": 1, "hasTable": False,
                "response": response.res,
                "execute_task": False}
    else:
        return {"status": 1, "hasTable": False,
                "response": response.res,
                "actions": response.actions,
                "execute_task": True}


@app.route("/reset", methods=["POST"])
def reset():
    manager.reset(request.json["uid"])
    return {"status": 1}


@app.route("/getDialog", methods=["GET"])
def get_dialogue():
    dialogue_id = request.args["dialog_id"]
    dialogue = manager.get_dialogue(dialogue_id)
    manager.current_dialog = dialogue_id
    return dialogue

@app.route("/getNewDialog", methods=["GET"])
def get_new_dialogue():
    uid = request.args["uid"]
    dialogue_id = 1
    manager.current_dialog = dialogue_id
    return {"status":1, "dialogue_id": dialogue_id}


@app.route("/getAllDialog", methods=["GET"])
def get_all_dialogue():
    dialogue = manager.get_all_dialogue("test")
    return {
        "dialog": dialogue,
        "status": 1
    }


@app.route("/getReviewDialog", methods=["GET"])
def get_review_dialog():
    dialogs = manager.get_review_dialog(request.args["uid"])
    return {
        "status": 1,
        "dialog": dialogs
    }


@app.route("/getReview", methods=["GET"])
def get_review():
    query = request.args
    uid = query["uid"]
    dialog_id = query["dialog"]
    turn = query["turn"]
    print(uid, dialog_id, turn)
    raw_img, return_img, actions, check_status, goals, lan_infos = manager.check_trace(uid, dialog_id, turn)
    goals = goals.strip("Goals:")
    goals = "<br>".join(goals.split("\n"))
    res = {
        "status": 1,
        "image": raw_img,
        "layout": return_img,
        "action": actions,
        "check_status": check_status,
        "goals": goals,
        "lan_infos": lan_infos,
    }
    # print(type(res))
    # print(type(res["image"][0]))
    # print(type(res["layout"][0]))
    # print(type(res["action"][0]))
    # print(res["action"])
    return res


@app.route("/goalsGenerator", methods=["GET"])
def goals_generator():
    goals, lan_infos = manager.generate_goals()
    goals = goals.strip("Goals:")
    goals = "<br>".join(goals.split("\n"))
    return {
        "goals": goals,
        "lan_infos": lan_infos,
        "status": 1,
    }


@app.route("/addDialog", methods=["GET"])
def add_dialog():
    query = request.args
    dialog_id = query["dialog"]
    turn = query["turn"]
    manager.add_dialog(dialog_id, turn)
    return {
        "status": 1
    }


@app.route("/deleteDialog", methods=["GET"])
def delete_dialog():
    query = request.args
    dialog_id = query["dialog"]
    turn = query["turn"]
    manager.delete_dialog(dialog_id, turn)
    return {
        "status": 1
    }


if __name__ == '__main__':
    app.run(debug=False)
    # data = get_dialogue()
