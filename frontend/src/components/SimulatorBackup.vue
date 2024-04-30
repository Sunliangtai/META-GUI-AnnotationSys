<template>
  <el-row>
    <el-col :span="12">
      <!-- <iframe
        src="https://appetize.io/embed/demo_r0m5r98axtdhftx1hmmhq1c0m8?device=nexus5&scale=70&deviceColor=white&screenOnly=false&centered=true&xdocMsg=true&record=true"
        width="300px"
        height="640px"
        frameborder="0"
        ref="iframe"
      ></iframe> -->
      <ImageSimulator
        :image="image || img"
        @swipe="swipe"
        @doubleTap="doubleTap"
        @singleTap="singleTap"
      ></ImageSimulator>
      <div>
        <el-button icon="el-icon-refresh" @click="restartApp"></el-button>
        <el-button
          icon="el-icon-video-play"
          @click="startRecording"
        ></el-button>
        <el-button icon="el-icon-video-pause" @click="endRecording"></el-button>
        <el-button icon="el-icon-camera" @click="getScreen"></el-button>
      </div>
    </el-col>
    <el-col :span="12">
      <div>
        <!-- <ImageSimulator
          :image="image"
          @swipe="swipe"
          @doubleTap="doubleTap"
          @singleTap="singleTap"
        ></ImageSimulator> -->
        <!-- <button @click="requestSession()">requestSession</button>
        <button @click="emitHomeButton()">emitHomeButton</button>
        <button @click="rotateLeft()">rotateLeft</button>
        <button @click="rotateRight()">rotateRight</button>
        <button @click="setScale(30)">setScale to 30%</button>
        <button @click="setScale(70)">setScale to 70%</button>
        <button @click="saveScreenshot()">saveScreenshot</button>
        <button @click="getUI">get ui</button>
        <button @click="getScreenshot()">getScreenshot</button>
        <button @click="heartbeat()">heartbeat</button>
        <button @click="mouseclick(160, 130)">mouseclick 160, 130</button>
        <button @click="pasteText('hello@appetize.io!')">
          pasteText hello@appetize.io!
        </button>
        <button @click="keypress('c', false)">keypress lowercase c</button>
        <button @click="keypress('c', true)">keypress uppercase C</button>
        <button @click="setLanguage('fr')">setLanguage to 'fr'</button>
        <button @click="setLocation([47.4925, 19.0513])">setLocation to Paris</button>
        <button @click="setLocation([39.903924, 116.391432])">seation to Beijing</button>
        <button @click="openUrl('https://appetize.io/')">openUrl Appetize.io</button>
        <button @click="openUrl('http://nytimes.com/')">openUrl NYTimes.com</button>
        <button @click="shakeDevice()">shakeDevice</button>
        <button @click="androidKeycodeMenu()">androidKeycodeMenu</button>
        <button @click="disableInteractions()">disableInteractions</button>
        <button @click="enableInteractions()">enableInteractions</button>
        <button @click="restartApp()">restartApp</button>
        <button @click="endSession()">endSession</button> -->
      </div>
    </el-col>
  </el-row>
</template>

<script>
import ImageSimulator from "./ImageSimulator.vue";

export default {
  name: "Simulator",
  mounted() {
    window.addEventListener("message", this.messageEventHandler, false);
  },
  props: ["img"],
  data() {
    return {
      image: null,
    };
  },
  methods: {
    startRecording() {
      this.$emit("start-record");
    },
    endRecording() {
      this.$emit("end-record");
    },
    playback(pb_obj) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "playEvent", value: pb_obj },
        "*"
      );
    },

    requestSession() {
      this.$refs.iframe.contentWindow.postMessage("requestSession", "*");
    },

    emitHomeButton() {
      this.$refs.iframe.contentWindow.postMessage("emitHomeButton", "*");
    },

    rotateLeft() {
      this.$refs.iframe.contentWindow.postMessage("rotateLeft", "*");
    },

    rotateRight() {
      this.$refs.iframe.contentWindow.postMessage("rotateRight", "*");
    },

    setScale(number) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "setScale", value: number },
        "*"
      );
    },

    saveScreenshot() {
      this.$refs.iframe.contentWindow.postMessage("saveScreenshot", "*");
    },

    getScreenshot() {
      this.$refs.iframe.contentWindow.postMessage("getScreenshot", "*");
    },

    getUI() {
      this.$refs.iframe.contentWindow.postMessage("dumpUi", "*");
    },

    getScreen() {
      this.getScreenshot();
      this.getUI();
    },

    heartbeat() {
      this.$refs.iframe.contentWindow.postMessage("heartbeat", "*");
    },

    mouseclick(x, y) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "mouseclick", x: x, y: y },
        "*"
      );
    },

    pasteText(textToPaste) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "pasteText", value: textToPaste },
        "*"
      );
    },

    swipe(touch) {
      this.$emit("swipe", touch);
    },

    singleTap(touch) {
      this.$emit("singleTap", touch);
    },

    doubleTap(touch) {
      this.$emit("doubleTap", touch);
    },

    keypress(key, shiftKey) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "keypress", key: key, shiftKey: shiftKey },
        "*"
      );
    },

    // must be supported by app to work
    setLanguage(language_code) {
      alert(
        "App must support language specified to work, default app does not"
      );
      this.$refs.iframe.contentWindow.postMessage(
        { type: "language", value: language_code },
        "*"
      );
    },

    // updates gps location in app
    setLocation(location) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "location", value: location },
        "*"
      );
    },

    // opens URL
    openUrl(url) {
      this.$refs.iframe.contentWindow.postMessage(
        { type: "url", value: url },
        "*"
      );
    },

    // ios only
    shakeDevice() {
      this.$refs.iframe.contentWindow.postMessage("shakeDevice", "*");
    },

    // android only
    androidKeycodeMenu() {
      this.$refs.iframe.contentWindow.postMessage("androidKeycodeMenu", "*");
    },

    disableInteractions() {
      this.$refs.iframe.contentWindow.postMessage("disableInteractions", "*");
    },

    enableInteractions() {
      this.$refs.iframe.contentWindow.postMessage("enableInteractions", "*");
    },

    restartApp() {
      this.$refs.iframe.contentWindow.postMessage("restartApp", "*");
    },

    endSession() {
      this.$refs.iframe.contentWindow.postMessage("endSession", "*");
    },

    messageEventHandler(event) {
      if (event.data.type == "recordedEvent") {
        console.log("recordedEvent", event.data.value.type);
        this.$emit("log-action", event);
      }
      // if (event.data.type == "deleteEvent") {
      //   this.$emit("delete-event", event);
      // }
      else if (
        event.data.type == "playbackFoundAndSent" ||
        event.data.type == "playbackError"
      ) {
        this.$emit("playback-result", event);
      } else if (event.data == "firstFrameReceived") {
        this.$emit("boosted");
      } else if (event.data == "sessionEnded") {
        this.$emit("end");
      } else if (event.data.type == "uiDump") {
        this.$emit("ui", event);
      } else if (event.data.type == "screenshot") {
        this.image = event.data.data;
        this.$emit("screenshot", event);
      }
    },
  },
  components: {
    ImageSimulator,
  },
};
</script>

<style>
button {
  margin-bottom: 10px;
}
</style>
