from utils import write_json, read_json


def get_actions(action_id):
    return read_json("./data/{}.json".format(action_id))


def save_actions(actions):
    action_id = actions["action_id"]
    write_json("./data/{}.json".format(action_id), actions)
