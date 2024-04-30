<template>
  <el-row>
    <el-col :span="8">
      <div class="dialog-main">
        <div class="dialog-header">
          <el-select
            @change="getDialog"
            v-model="current_dialog"
            value-key="name"
            placeholder="对话id"
          >
            <el-option
              v-for="(item, index) in dialog_list"
              :key="index"
              :label="item.name"
              :value="item"
            >
              <span style="float: left">{{ item.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">{{
                item.check_status
              }}</span>
            </el-option>
          </el-select>
          当前轮数:{{ current_turn }}
          <el-button type="success" @click="saveImages(1)"
            >通过 <i class="el-icon-check"></i
          ></el-button>
          <el-button type="danger" @click="saveImages(0)"
            >不通过 <i class="el-icon-close"></i
          ></el-button>
        </div>
        <el-button-group>
          <el-button type="primary" @click="lastTurn"> 上一轮 </el-button>
          <el-button type="primary" @click="nextTurn"> 下一轮 </el-button>
          <!-- <el-button type="danger" @click="endRecording"
            >结束录制 <i class="el-icon-video-pause"></i
          ></el-button> -->
          <!-- <el-button type="success" @click="saveImages"
            >保存 <i class="el-icon-video-pause"></i
          ></el-button> -->
          <el-button type="warning" @click="changeViewMode"
            >切换审核模式 <i class="el-icon-refresh"></i
          ></el-button>
          <el-button type="plain" @click="changeViewLayout"
            >切换图片模式 <i class="el-icon-refresh"></i
          ></el-button>
        </el-button-group>
        <div id="dialog-window" class="dialog-dialog">
          <Talk
            v-for="(item, index) in dialog"
            :data="item"
            :key="index"
            :index="index"
            :selected="
              index >= current_turn * 2 && index <= current_turn * 2 + 1
            "
            @editTurn="editTurn"
            @inputFocus="setInputFocus"
          ></Talk>
        </div>
      </div>
    </el-col>

    <el-col :span="16" v-if="viewmode">
      <ImageList ref="imageList" :bigger="true" v-loading="loading"></ImageList>
    </el-col>

    <el-col :span="10" v-if="!viewmode">
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

    <el-col :span="6" v-if="!viewmode">
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
  net_save_review,
  net_reset,
  net_get_review,
  net_get_review_dialog,
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
      current_dialog: null,
      current_user: "test",
      current_turn: 0,
      dialog_list: [],
      raw_images: [],
      layout_images: [],
      viewmode: true,
      loading: false,
      viewLayout: false,
    };
  },
  // updated: function () {
  //   let body = document.getElementById("dialog-window");
  //   body.scrollTop = body.scrollHeight;
  // },
  async mounted() {
    // this.send_message("reset");
    // await net_reset({ uid: this.current_user });
    await net_reset({ uid: this.current_user });
    let response = await net_get_review_dialog({ uid: this.current_user });
    console.log(response);
    if (response["status"] == 1) {
      this.setNotice("已获取对话。");
      let first = -1;
      for (let i = 0; i < response["dialog"].length; i++) {
        let item = response["dialog"][i];
        if (item.check_status == 1) item.check_status = "通过";
        else if (item.check_status == 0) item.check_status = "未通过";
        else {
          item.check_status = "";
          if (first == -1) first = i;
        }
      }
      if (first == -1) first = 0;
      this.dialog_list = response["dialog"];
      this.current_dialog_id = this.dialog_list[first].dialog_id;
      this.current_dialog = this.dialog_list[first];
      this.getDialog(this.current_dialog);
    }
    document.body.addEventListener("keydown", this.handleSpace);
  },
  methods: {
    changeViewLayout() {
      this.viewLayout = !this.viewLayout;
      this.getImages();
    },
    changeViewMode() {
      this.viewmode = !this.viewmode;
      if (this.viewmode) {
        this.getImages();
      }
    },
    editTurn(turn_index, text) {
      let origin = this.dialog[turn_index];
      origin.text = text;
      console.log(origin);
      this.dialog.splice(turn_index, 1, origin);
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
      if (this.viewmode) return;
      this.$refs.simulator.setNotice(notice);
    },
    async saveImages(result) {
      let note = "";
      if (result == 1)
        note =
          "将当前对话标记为通过，保存所有标注的图片并加载下一轮对话，是否继续？";
      else note = "将当前对话标记为不通过并加载下一轮对话，是否继续？";
      this.$confirm(note, "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }).then(async () => {
        if (result == 1) this.current_dialog.check_status = "通过";
        else this.current_dialog.check_status = "未通过";
        let saved_image = this.$refs.imageList.get_saved_image();
        let data = {
          screens: saved_image,
          dialog: this.dialog,
          trace: this.current_dialog.name,
          turn: this.current_turn,
          check_status: result,
        };
        let response = await net_save_review(data);
        if (response["status"] == 1) {
          this.setNotice("保存成功");
          this.nextTurn();
        }
      });
    },
    async setImage() {
      this.$refs.imageList.add_image(
        this.shown_images[0][0],
        this.shown_images[0][1]
      );
      for (let i = 1; i < this.shown_images.length; i++) {
        await this.$refs.imageList.add_image(
          this.shown_images[i][0],
          this.shown_images[i][1],
          this.action[i - 1]["action"],
          this.action[i - 1]["text"],
          this.action[i - 1]
        );
      }
    },
    async getImages() {
      this.$refs.imageList.clear_image();
      this.loading = true;
      let params = {
        uid: this.current_user,
        dialog: this.current_dialog_id,
        turn: this.current_turn,
      };
      console.log("get image", params);
      let response = await net_get_review(params);
      if (response["status"] == 1) {
        this.raw_images = response["image"];
        this.layout_images = response["layout"];
        this.action = response["action"];
        this.setImage();
      }
      this.loading = false;
    },
    getDialog(dialog) {
      this.current_dialog_id = dialog.dialog_id;
      this.current_dialog = dialog;
      this.current_turn = 0;
      this.dialog = [];
      for (let i = 0; i < this.current_dialog.dialog.length; i++) {
        let message = this.current_dialog.dialog[i];
        this.update_history(message, message.isUser);
      }
      this.getImages();
      console.log("change to", this.current_dialog);
    },
    lastTurn() {
      this.setNotice("正在切换至上一轮对话。");
      if (this.current_turn == 0) return;
      this.current_turn -= 1;
      this.getImages();
    },
    nextTurn() {
      this.setNotice("正在切换至下一轮对话。");
      let next_index = (this.current_turn + 1) * 2;
      if (next_index < this.current_dialog.dialog.length) {
        this.current_turn += 1;
        // 获取下一轮的图片
        this.getImages();
      } else {
        this.enable_save = false;
        this.$alert("当前对话已经检查完毕，即将跳转到下一个对话。", "已完成", {
          confirmButtonText: "确定",
          callback: () => {
            let idx = -1;
            // for (let i = 0; i < this.dialog_list.length; i++)
            //   if (this.dialog_list[i].dialog_id == this.current_dialog_id) {
            //     idx = i;
            //     break;
            //   }
            // this.dialog_list.splice(idx, 1);
            for (let i = 0; i < this.dialog_list.length; i++)
              if (this.dialog_list[i].check_status == "") {
                idx = i;
                break;
              }
            if (idx == -1) idx = 0;
            this.current_dialog_id = this.dialog_list[idx].dialog_id;
            this.current_dialog = this.dialog_list[idx];
            this.getDialog(this.current_dialog);
            this.$refs.imageList.clear_image();
          },
        });
      }
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
      if (this.viewmode) return;
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
  computed: {
    shown_images() {
      if (this.viewLayout) return this.layout_images;
      else return this.raw_images;
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
