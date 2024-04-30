<template>
  <el-row>
    <el-col :span="8">
      <div class="dialog-main">
        <!-- <div class="dialog-header">状态：{{ status }}</div> -->
        <el-button-group>
          <el-button
            type="primary"
            @click="getDialog"
            :disabled="!enable_change_dialog"
            >换个对话 <i class="el-icon-refresh"></i
          ></el-button>
          <el-button type="success" @click="startRecording"
            >开始录制 <i class="el-icon-video-play"></i
          ></el-button>
          <!-- <el-button type="danger" @click="endRecording"
            >结束录制 <i class="el-icon-video-pause"></i
          ></el-button> -->
          <el-button type="success" @click="saveImages" :disabled="!enable_save"
            >保存 <i class="el-icon-video-pause"></i
          ></el-button>
        </el-button-group>
        <div id="dialog-window" class="dialog-dialog">
          <Talk
            v-for="(item, index) in dialog"
            :data="item"
            :key="index"
            :index="index"
            @editTurn="editTurn"
            @inputFocus="setInputFocus"
          ></Talk>
        </div>
        <!-- <div class="dialog-input">
          <el-input
            placeholder="请输入内容"
            v-model="input"
            class="dialog-input-box"
            @keyup.enter.native="submit"
          >
            <el-button
              slot="append"
              icon="el-icon-s-promotion"
              type="success"
              @click="submit"
            ></el-button>
          </el-input>
        </div> -->
      </div>
    </el-col>

    <el-col :span="10">
      <ImageSimulator
        @swipe="swipe"
        @doubleTap="doubleTap"
        @singleTap="singleTap"
        @getScreen="getScreenshot"
        @goBack="goBack"
        @input="inputText"
        @inputFocus="setInputFocus"
        @clear="clearInput"
        @read="readBox"
        @inputChar="inputChar"
        :image="image"
        ref="simulator"
      ></ImageSimulator>
    </el-col>

    <el-col :span="6">
      <ImageList ref="imageList"></ImageList>
    </el-col>
  </el-row>
</template>

<script>
import Talk from "./Talk";
import ImageSimulator from "../ImageSimulator.vue";
import ImageList from "../ImageList.vue";
import {
  net_get_response,
  net_do_action,
  net_get_screenshot,
  net_get_dialog,
  net_start_record,
  net_end_record,
  net_save,
  net_reset,
} from "@/network";

// function sleep(time) {
//   return new Promise((resolve) => setTimeout(resolve, time));
// }

export default {
  name: "Dialog",
  data() {
    return {
      input: "",
      status: "等待输入",
      input_focus: false,
      dialog: [],
      full_dialog: [],
      image: null,
      enable_interact: false,
      last_action: {},
      recording: false,
      enable_change_dialog: true,
      enable_save: false,
      current_dialog_id: null,
      current_user: "test",
    };
  },
  updated: function () {
    let body = document.getElementById("dialog-window");
    body.scrollTop = body.scrollHeight;
  },
  mounted() {
    // this.send_message("reset");
    // await net_reset({ uid: this.current_user });
    this.getDialog();
    document.body.addEventListener("keydown", this.handleSpace);
    net_reset({ uid: this.current_user });
  },
  methods: {
    editTurn(turn_index, text) {
      let origin = this.full_dialog[turn_index];
      origin.text = text;
      console.log(origin);
      this.full_dialog.splice(turn_index, 1, origin);
    },
    setInputFocus(focus) {
      this.input_focus = focus;
      if (focus) document.body.removeEventListener("keydown", this.handleSpace);
      else document.body.addEventListener("keydown", this.handleSpace);
    },
    handleSpace() {
      let key = window.event.keyCode;
      if (key == 32) {
        window.event.preventDefault();
        this.$refs.simulator.getScreen();
      }
    },
    setNotice(notice) {
      this.$refs.simulator.setNotice(notice);
    },
    async saveImages() {
      this.$confirm(
        "将保存所有标注的图片并加载下一轮对话，是否继续？",
        "提示",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      ).then(async () => {
        let saved_image = this.$refs.imageList.get_saved_image();
        let data = { screens: saved_image, dialog: this.full_dialog };
        let response = await net_save(data);
        if (response["status"] == 1) {
          this.setNotice("保存成功");
          this.getNextTurn();
        }
      });
    },
    async startRecording() {
      this.enable_interact = true;
      this.recording = true;
      this.enable_change_dialog = false;
      this.enable_save = true;
      if (this.current_turn == 0) {
        this.dialog = [];
        for (let i = 0; i < 2; i++) {
          let message = this.full_dialog[i];
          this.update_history(message, message.isUser);
        }
      }
      let res = await net_start_record({ uid: this.current_user });
      if (res["status"] == 1) {
        this.setNotice("开始录制，请在网页上操作手机，所有操作将会被记录。");
        this.$message({
          message: "开始录制",
          type: "success",
        });
      }
    },
    async endRecording() {
      let res = await net_end_record({
        uid: this.current_user,
        dialog: this.current_dialog_id,
      });
      if (res["status"] == 1) {
        this.setNotice("结束录制，请在右侧确认截图列表。");
        this.$message({
          message: "录制成功",
          type: "success",
        });
      }
      this.recording = false;
    },
    async getDialog() {
      this.setNotice("获取对话中");
      let response = await net_get_dialog({ turn: 0 });
      if (response["status"] == 1) {
        this.setNotice(
          "已获取对话，可根据对话在手机上探索，准备好后点击开始录制进行操作录制。"
        );
        this.current_dialog_id = response["id"];
        this.full_dialog = response["turns"];
        this.dialog = [];
        for (let i = 0; i < response["turns"].length; i++) {
          let message = response["turns"][i];
          this.update_history(message, message.isUser);
        }
        this.current_dialog_id = response["id"];
        this.current_turn = 0;
      } else {
        this.setNotice("所有对话已经标注完毕。")
        this.$message("所有对话已经标注完毕。")
      }
    },
    getNextTurn() {
      this.setNotice("正在获取下一轮对话。");
      console.log(this.current_turn);
      console.log(this.full_dialog);
      let next_index = (this.current_turn + 1) * 2;
      if (next_index < this.full_dialog.length) {
        this.current_turn += 1;
        for (let i = next_index; i < next_index + 2; i++) {
          let message = this.full_dialog[i];
          this.update_history(message, message.isUser);
        }
        this.setNotice(
          "已获取对话，可根据对话在手机上探索，准备好后点击开始录制进行操作录制。"
        );
      } else {
        this.enable_change_dialog = true;
        this.enable_save = false;
        this.$alert("当前对话已经标注完毕，即将跳转到下一个对话。", "已完成", {
          confirmButtonText: "确定",
          callback: async () => {
            let response = await net_end_record({"uid": this.current_user});
            if (response["status"] == 1) this.getDialog();
          },
        });
      }
      this.$refs.imageList.clear_image();
      this.getScreenshot();
    },
    async clearInput() {
      if (!this.enable_interact) return;
      this.setNotice("清除输入执行中");
      let action = { type: "clear" };
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        // this.getScreenshot();
        this.setNotice(
          "清除输入执行完毕，请点击截图按钮或者使用空格键进行截图。"
        );
        this.last_action = { op: "清除输入", note: "", touch: null };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },
    async inputChar(c) {
      if (!this.enable_interact) return;
      let name = "";
      if (c == "space") name = "空格";
      else name = "回车";
      this.setNotice("输入" + name);
      let action = { type: c };
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        // this.getScreenshot();
        this.setNotice(
          "已输入" + name + ", 请点击截图按钮或者使用空格键进行截图。"
        );
        this.last_action = { op: name, note: "", touch: null };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },
    async readBox(box) {
      if (!this.enable_interact) return;
      this.setNotice("添加读取框中");
      let action = {
        type: "read",
        height: box.height,
        width: box.width,
        top: box.top,
        left: box.left,
      };
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      // let response = { status: 1 };
      if (response["status"] == 1) {
        // this.getScreenshot();
        this.setNotice("已添加读取框，请点击截图按钮或者使用空格键进行截图。");
        this.last_action = { op: "读取", note: "", touch: box };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },
    async inputText(e) {
      if (!this.enable_interact) return;
      this.setNotice("输入文字执行中");
      let action = { type: "input", text: e };
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        // this.getScreenshot();
        this.setNotice(
          "输入文字完成，输入内容：" +
            e +
            "，请点击截图按钮或者使用空格键进行截图。"
        );
        this.last_action = { op: "输入", note: e, touch: null };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },
    async goBack() {
      if (!this.enable_interact) return;
      this.setNotice("执行返回键");
      let action = { type: "back" };
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        this.setNotice("返回执行完毕，请点击截图按钮或者使用空格键进行截图。");
        this.last_action = { op: "返回", note: "", touch: null };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },
    async swipe(touch) {
      if (!this.enable_interact) return;
      this.setNotice("执行滑动操作。");
      console.log("swipe", touch);
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let action = {
        type: "swipe",
        x1: touch.x1,
        y1: touch.y1,
        x2: touch.x2,
        y2: touch.y2,
      };
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        let direction = this.$refs.simulator.swipeDirection(
          touch.x1,
          touch.x2,
          touch.y1,
          touch.y2
        );
        this.setNotice(
          direction + "滑执行完毕，请点击截图按钮或者使用空格键进行截图。"
        );
        this.last_action = { op: direction + "滑", note: "", touch: null };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(action, "done");
      }
    },

    async singleTap(touch) {
      if (!this.enable_interact) return;
      this.setNotice("点击执行中");
      console.log("single tap", touch);
      this.$refs.simulator.setLoading(true);
      this.enable_interact = false;
      let action = { type: "click", x: touch.x1, y: touch.y1 };
      let response = await net_do_action({
        uid: this.current_user,
        action: action,
      });
      if (response["status"] == 1) {
        this.setNotice(
          "点击执行完毕，点击位置：" +
            touch.x1 +
            "," +
            touch.y1 +
            ",请点击截图按钮或者使用空格键进行截图。"
        );
        this.last_action = {
          op: "点击",
          note: "点击位置：" + touch.x1 + "," + touch.y1,
          touch: touch,
        };
        this.$refs.simulator.setLoading(false);
        this.enable_interact = true;
        console.log(this.enable_interact);
        console.log(action, "done");
      }
    },

    doubleTap(touch) {
      console.log("double tap", touch);
    },

    async getScreenshot() {
      this.enable_interact = false;
      this.setNotice("获取截图中，请勿进行操作。");
      this.$refs.simulator.setLoading(true);
      let response = await net_get_screenshot({ uid: this.current_user });
      console.log(response);
      if (response["status"] == 1) {
        this.setNotice("获取截图完毕，可以进行下一步操作。");
        this.$refs.simulator.setImage(response["screenshot"]);
        this.$refs.imageList.add_image(
          response["screenshot"],
          response["screen_id"],
          this.last_action["op"],
          this.last_action["note"],
          this.last_action["touch"]
        );
        this.$refs.simulator.setLoading(false);
      }
      this.enable_interact = true;
    },

    update_history(new_msg, isUser) {
      new_msg["isUser"] = isUser;
      this.dialog.push(new_msg);
    },
    async send_message(text, data = null) {
      console.log("send", text);
      let response = await net_get_response({
        message: text,
        data: data,
      });
      console.log("receive:", response);
      // let response = {'response':'收到：'+text,'session':this.$store.state.user.session+'1'};
      if (response["status"] == 1) {
        if (response["execute_task"]) {
          if (!this.playback_status.has_loaded) {
            this.update_history({ text: response["response"] }, false);
            this.status = "begin to perform task";
            this.playback_status.has_loaded = true;
            if (this.session_on) {
              this.$refs.simulator.endSession();
            }
            this.$refs.simulator.requestSession();
          }
          return;
        }

        this.update_history({ text: response["response"] }, false);
        this.status = "success";
      } else {
        this.status = "fail";
      }
    },
    submit() {
      let text = this.input;
      if (!text) return;
      this.status = "updating dom";
      this.input = "";
      this.update_history({ text: text }, true);
      this.status = "sending message";
      console.log(text);
      // 特殊处理
      if (text.startsWith("输入")) {
        let input_text = text.slice(2);
        console.log("输入：", input_text);
        this.$refs.simulator.pasteText(input_text);
        return;
      }
      this.send_message(text);
    },
  },
  components: {
    Talk,
    ImageSimulator,
    ImageList,
  },
};
</script>

<style scoped>
.dialog-main {
  background-color: white;
  width: 90%;
  height: 650px;
  border-radius: 10px;
  border: 1px gray solid;
  overflow: hidden;
}

.dialog-header {
  border-bottom: 1px gray solid;
  height: 8%;
  padding: 5px 0 0 10px;
}

.dialog-dialog {
  height: 84%;
  overflow-y: auto;
  overflow-x: hidden;
}

.dialog-input {
  height: 8%;
  overflow: hidden;
  display: flex;
  flex-direction: column-reverse;
}

.dialog-tag {
  height: 30px;
  width: 50px;
  margin: 10px 0 10px 10px;
}
.name-input {
  width: 30%;
}
</style>
