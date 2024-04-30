from utils import read_json, write_json, read_file
import os

data_path = "./data/user_test"
traces = os.listdir(data_path)
traces = sorted(traces, key=lambda t: int(t.split("_")[-1]))
dialogs = []
annotated_dialog = []
for trace in traces:
    dialog = read_json(os.path.join(data_path, trace, "dialogue.json"))
    dialog_id = read_file(os.path.join(data_path, trace, "dialogue_id.txt"))
    dialogs.append({
        "id": dialog_id,
        "turns": dialog
    })
    annotated_dialog.append(dialog_id)

write_json(os.path.join("./data/dialog_data", "SMCalFlow_extracted_data.json"), dialogs)
write_json(os.path.join("./data", "annotated_data.json"), annotated_dialog)
