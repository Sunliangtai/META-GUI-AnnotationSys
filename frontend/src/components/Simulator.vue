<template>
  <el-row>
    <el-col :span="12">
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
    swipe(touch) {
      this.$emit("swipe", touch);
    },

    singleTap(touch) {
      this.$emit("singleTap", touch);
    },

    doubleTap(touch) {
      this.$emit("doubleTap", touch);
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
