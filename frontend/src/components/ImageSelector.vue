<template>
  <div
    @mousedown="handleMouseDown"
    class="selector-box"
    :width="width"
    :height="height"
  >
    <div class="mask" :style="bbox"></div>
    <img class="image" :src="image" :width="width" :height="height" />
  </div>
</template>

<script>
export default {
  // https://segmentfault.com/a/1190000023072352
  name: "ImageSelector",
  props: ["image", "width", "height"],
  data() {
    return {
      start_x: 0,
      start_y: 0,
      end_x: 0,
      end_y: 0,
      compute_size: false,
    };
  },
  methods: {
    handleMouseDown(event) {
      event.preventDefault();
      //   this.resSetXY();
      this.compute_size = false;
      this.start_x = event.offsetX;
      this.start_y = event.offsetY;

      document.body.addEventListener("mousemove", this.handleMouseMove);
      document.body.addEventListener("mouseup", this.handleMouseUp);
    },
    handleMouseMove(event) {
      this.compute_size = true;
      this.end_x = event.offsetX;
      this.end_y = event.offsetY;
    },
    handleMouseUp() {
      document.body.removeEventListener("mousemove", this.handleMouseMove);
      document.body.removeEventListener("mouseup", this.handleMouseUp);
      this.$emit("box", {
        width: this.mask_width,
        height: this.mask_height,
        top: this.mask_top,
        left: this.mask_left,
      });
    },
    resSetXY() {
      this.start_x = 0;
      this.start_y = 0;
      this.end_x = 0;
      this.end_y = 0;
    },
  },
  computed: {
    mask_top: function () {
      return this.start_y < this.end_y ? this.start_y : this.end_y;
    },
    mask_left: function () {
      return this.start_x < this.end_x ? this.start_x : this.end_x;
    },
    mask_width: function () {
      return Math.abs(this.start_x - this.end_x);
    },
    mask_height: function () {
      return Math.abs(this.start_y - this.end_y);
    },
    bbox: function () {
      if (this.compute_size) {
        let box =
          "width:" +
          this.mask_width +
          "px;left:" +
          this.mask_left +
          "px;height:" +
          this.mask_height +
          "px;top:" +
          this.mask_top +
          "px;";
        return box;
      } else {
        return (
          "width:" +
          0 +
          "px;left:" +
          0 +
          "px;height:" +
          0 +
          "px;top:" +
          0 +
          "px;"
        );
      }
    },
  },
};
</script>

<style scoped>
.selector-box {
  position: relative;
  background: gray;
}
.mask {
  position: absolute;
  background: white;
  opacity: 1;
}
.image {
  opacity: 0.8;
}
</style>