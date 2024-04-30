<template>
  <div>
    <el-row>
      <el-col :span="12">
        <div v-loading="loading" :style="{ width: width, height: height }">
          <ImageSelector
            v-if="enable_select"
            :image="image"
            :width="width"
            :height="height"
            @box="getImageBox"
          ></ImageSelector>
          <img
            v-else
            :src="image"
            ref="image"
            id="screen"
            :width="width"
            :height="height"
            draggable="false"
            @touchstart="touchstart"
            @MSPointerDown="touchstart"
            @pointerdown="touchstart"
            @touchmove="touchmove"
            @MSPointerMove="touchmove"
            @pointermove="touchmove"
            @touchend="touchend"
            @MSPointerUp="touchend"
            @pointerup="touchend"
            @touchcancel="cancelAll"
            @MSPointerCancel="cancelAll"
            @pointercancel="cancelAll"
          />
        </div>
      </el-col>
      <el-col :span="10">
        <el-card :style="{ marginBottom: '10px' }">
          <div slot="header" class="clearfix">
            <span>状态提示</span>
          </div>
          <div>{{ notice }}</div>
        </el-card>
        <el-card>
          <div slot="header" class="clearfix">
            <span>操作</span>
          </div>
          <div class="dialog-input">
            <el-input
              placeholder="请输入内容"
              v-model="input"
              @focus="changeFocus(true)"
              @blur="changeFocus(false)"
              @keyup.enter.native="inputText"
            >
              <el-button
                slot="append"
                icon="el-icon-s-promotion"
                type="success"
                @click="inputText"
              ></el-button>
            </el-input>
          </div>
          <el-button-group :style="{ marginTop: '10px' }">
            <el-button icon="el-icon-back" @click="swipeButton('left')"
              >左滑</el-button
            >
            <el-button icon="el-icon-right" @click="swipeButton('right')"
              >右滑</el-button
            >
            <el-button icon="el-icon-top" @click="swipeButton('up')"
              >上滑</el-button
            >
            <el-button icon="el-icon-bottom" @click="swipeButton('down')"
              >下滑</el-button
            >
            <el-button icon="el-icon-back" @click="goBack">返回</el-button>
            <!-- <el-button @click="inputChar('space')">空格</el-button> -->
            <el-button icon="el-icon-check" @click="inputChar('enter')"
              >回车</el-button
            >
            <el-button icon="el-icon-check" @click="home"
              >返回桌面</el-button
            >
            <el-button type="plain" @click="clear">清除输入</el-button>
          </el-button-group>
          <el-button-group :style="{ marginTop: '10px', marginBottom: '10px' }">
            <el-button icon="el-icon-view" @click="readBox">读取</el-button>
            <el-button icon="el-icon-view" @click="confirmBox"
              >读取确认</el-button
            >
          </el-button-group>
          <el-button icon="el-icon-camera" @click="getScreen" type="primary">截图</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import ImageSelector from "./ImageSelector.vue";
export default {
  name: "ImageSimulator",
  data() {
    return {
      touch: {},
      touchTimeout: null,
      tapTimeout: null,
      swipeTimeout: null,
      longTapTimeout: null,
      longTapDelay: 750,
      gesture: null,

      now: null,
      delta: 0,
      deltaX: 0,
      deltaY: 0,
      firstTouch: null,
      isPointerType: false,

      screen_width: 1440,
      screen_height: 2560,
      scale: 0.25,

      image: null,
      loading: false,
      input: "",

      enable_select: false,
      image_box: null,

      notice: "",
    };
  },
  computed: {
    width: function () {
      return this.screen_width * this.scale + "px";
    },
    height: function () {
      return this.screen_height * this.scale + "px";
    },
  },
  mounted: function () {
    this.$emit("getScreen", "init");
    this.loading = true;
  },
  methods: {
    changeFocus(focus) {
      this.$emit("inputFocus", focus);
    },
    setNotice(notice) {
      this.notice = notice;
    },
    setLoading(loading) {
      this.loading = loading;
    },
    getImageBox(box) {
      this.image_box = box;
      console.log(box);
    },
    inputText() {
      if (this.input == "") return;
      this.$emit("input", this.input);
      this.input = "";
      // this.loading = true;
    },
    setImage(image) {
      this.image = image;
      this.loading = false;
    },
    readBox() {
      this.enable_select = true;
    },
    inputChar(c) {
      this.$emit("inputChar", c);
    },
    confirmBox() {
      if (!this.image_box) return;
      this.enable_select = false;
      this.image_box.height = Math.trunc(this.image_box.height / this.scale);
      this.image_box.width = Math.trunc(this.image_box.width / this.scale);
      this.image_box.top = Math.trunc(this.image_box.top / this.scale);
      this.image_box.left = Math.trunc(this.image_box.left / this.scale);
      this.$emit("read", this.image_box);
    },
    clear() {
      this.$emit("clear");
      // this.loading = true;
    },
    getScreen() {
      this.$emit("getScreen");
      this.loading = true;
    },
    goBack() {
      this.$emit("goBack");
      // this.loading = true;
    },
    home(){
      this.$emit("home");
    },
    swipeButton(direction) {
      let middle_x = Math.trunc(this.screen_width / 2);
      let middle_y = Math.trunc(this.screen_height / 2);
      let up = Math.trunc(this.screen_height / 3);
      let down = Math.trunc((this.screen_height / 3) * 2);
      let right = Math.trunc((this.screen_width / 3) * 2);
      let left = Math.trunc(this.screen_width / 3);
      if (direction == "left")
        this.$emit("swipe", {
          x1: right,
          x2: left,
          y1: middle_y,
          y2: middle_y,
        });
      else if (direction == "right")
        this.$emit("swipe", {
          x1: left,
          x2: right,
          y1: middle_y,
          y2: middle_y,
        });
      else if (direction == "up")
        this.$emit("swipe", { x1: middle_x, x2: middle_x, y1: down, y2: up });
      else
        this.$emit("swipe", { x1: middle_x, x2: middle_x, y1: up, y2: down });
      console.log(direction);
    },
    // https://github.com/qianlongo/zepto-analysis/issues/13
    swipeDirection(x1, x2, y1, y2) {
      /**
       * 1. 第一个三元运算符得到如果x轴滑动的距离比y轴大，那么是左右滑动，否则是上下滑动
       * 2. 如果是左右滑动，起点比终点大那么往左滑动
       * 3. 如果是上下滑动，起点比终点大那么往上滑动
       * 需要注意的是这里的坐标和数学中的有些不一定 纵坐标有点反过来的意思
       * 起点p1(1, 0) 终点p2(1, 1)
       */
      return Math.abs(x1 - x2) >= Math.abs(y1 - y2)
        ? x1 - x2 > 0
          ? "左"
          : "右"
        : y1 - y2 > 0
        ? "上"
        : "下";
    },
    longTap() {
      this.longTapTimeout = null;
      if (this.touch.last) {
        // 触发el元素的longTap事件
        this.touch.el.trigger("longTap");
        this.touch = {};
      }
    },
    // 取消长按
    cancelLongTap() {
      if (this.longTapTimeout) clearTimeout(this.longTapTimeout);
      this.longTapTimeout = null;
    },

    // 取消所有事件
    cancelAll() {
      if (this.touchTimeout) clearTimeout(this.touchTimeout);
      if (this.tapTimeout) clearTimeout(this.tapTimeout);
      if (this.swipeTimeout) clearTimeout(this.swipeTimeout);
      if (this.longTapTimeout) clearTimeout(this.longTapTimeout);
      this.touchTimeout =
        this.tapTimeout =
        this.swipeTimeout =
        this.longTapTimeout =
          null;
      this.touch = {};
    },
    isPointerEventType(e, type) {
      return (
        e.type == "pointer" + type || e.type.toLowerCase() == "mspointer" + type
      );
    },
    isPrimaryTouch(event) {
      return (
        (event.pointerType == "mouse" ||
          event.pointerType == event.MSPOINTER_TYPE_TOUCH) &&
        event.isPrimary
      );
    },
    touchstart(e) {
      if (
        (this.isPointerType = this.isPointerEventType(e, "down")) &&
        !this.isPrimaryTouch(e)
      )
        return;
      // 如果是pointerdown事件则firstTouch保存为e，否则是e.touches第一个
      this.firstTouch = this.isPointerType ? e : e.touches[0];
      // 一般情况下，在touchend或者cancel的时候，会将其清除，如果用户调阻止了默认事件，则有可能清空不了
      if (e.touches && e.touches.length === 1 && this.touch.x2) {
        // Clear out touch movement data if we have it sticking around
        // This can occur if touchcancel doesn't fire due to preventDefault, etc.
        this.touch.x2 = undefined;
        this.touch.y2 = undefined;
      }
      // 保存当前时间
      this.now = Date.now();
      // 保存两次点击时候的时间间隔，主要用作双击事件
      this.delta = this.now - (this.touch.last || this.now);
      // touch.el 保存目标节点
      // 不是标签节点则使用该节点的父节点，注意有伪元素
      this.touch.el = this.$refs.image;
      // touchTimeout 存在则清除之，可以避免重复触发
      this.touchTimeout && clearTimeout(this.touchTimeout);
      // 记录起始点坐标（x1, y1）（x轴，y轴）
      this.touch.x1 = this.firstTouch.offsetX;
      this.touch.y1 = this.firstTouch.offsetY;
      // 两次点击的时间间隔 > 0 且 < 250 毫秒，则当做doubleTap事件处理
      if (this.delta > 0 && this.delta <= 250) this.touch.isDoubleTap = true;
      // 将now设置为touch.last，方便上面可以计算两次点击的时间差
      this.touch.last = this.now;
      // longTapDelay(750毫秒)后触发长按事件
      this.longTapTimeout = setTimeout(this.longTap, this.longTapDelay);
    },
    touchmove(e) {
      if (
        (this.isPointerType = this.isPointerEventType(e, "move")) &&
        !this.isPrimaryTouch(e)
      )
        return;
      if (!this.touch.x1) return;
      this.firstTouch = this.isPointerType ? e : e.touches[0];
      // 取消长按事件，都移动了，当然不是长按了
      this.cancelLongTap();
      // 终点坐标 (x2, y2)
      this.touch.x2 = this.firstTouch.offsetX;
      this.touch.y2 = this.firstTouch.offsetY;
      // 分别记录X轴和Y轴的变化量
      this.deltaX += Math.abs(this.touch.x1 - this.touch.x2);
      this.deltaY += Math.abs(this.touch.y1 - this.touch.y2);
    },
    touchend(e) {
      if (
        (this.isPointerType = this.isPointerEventType(e, "up")) &&
        !this.isPrimaryTouch(e)
      )
        return;

      // 取消长按事件
      this.cancelLongTap();
      // 滑动事件，只要X轴或者Y轴的起始点和终点的距离超过30则认为是滑动，并触发滑动(swip)事件,
      // 紧接着马上触发对应方向的swip事件（swipLeft, swipRight, swipUp, swipDown）
      // swipe
      if (
        (this.touch.x2 && Math.abs(this.touch.x1 - this.touch.x2) > 30) ||
        (this.touch.y2 && Math.abs(this.touch.y1 - this.touch.y2) > 30)
      )
        this.swipeTimeout = setTimeout(() => {
          if (this.touch.el) {
            this.$emit("swipe", this.resetTouch(this.touch));
            // this.loading = true;
          }
          this.touch = {};
        }, 0);
      // touch对象的last属性，在touchstart事件中添加，所以触发了start事件便会存在
      // normal tap
      else if ("last" in this.touch)
        if (this.deltaX < 30 && this.deltaY < 30) {
          // don't fire tap when delta position changed by more than 30 pixels,
          // for instance when moving to a point and back to origin
          // 只有当X轴和Y轴的变化量都小于30的时候，才认为有可能触发tap事件
          // delay by one tick so we can cancel the 'tap' event if 'scroll' fires
          // ('tap' fires before 'scroll')
          this.tapTimeout = setTimeout(() => {
            // trigger universal 'tap' with the option to cancelTouch()
            // (cancelTouch cancels processing of single vs double taps for faster 'tap' response)
            // 创建自定义事件
            //   var event = $.Event("tap");
            // 往自定义事件中添加cancelTouch回调函数，这样使用者可以通过该方法取消所有的事件
            //   event.cancelTouch = cancelAll;
            // [by paper] fix -> "TypeError: 'undefined' is not an object (evaluating 'touch.el.trigger'), when double tap
            // 当目标元素存在，触发tap自定义事件

            // trigger double tap immediately
            // 如果是doubleTap事件，则触发之，并清除touch
            if (this.touch.isDoubleTap) {
              if (this.touch.el) {
                this.$emit("doubleTap", this.resetTouch(this.touch));
              }
              this.touch = {};
            }

            // trigger single tap after 250ms of inactivity
            // 否则在250毫秒之后。触发单击事件
            else {
              this.touchTimeout = setTimeout(() => {
                this.touchTimeout = null;
                if (this.touch.el) {
                  this.$emit("singleTap", this.resetTouch(this.touch));
                  // this.loading = true;
                }
                this.touch = {};
              }, 250);
            }
          }, 0);
        } else {
          // 不是tap相关的事件
          this.touch = {};
        }
      // 最后将变化量信息清空
      this.deltaX = this.deltaY = 0;
    },
    resetTouch(touch) {
      touch.x1 = Math.trunc(touch.x1 / this.scale);
      touch.x2 = Math.trunc(touch.x2 / this.scale);
      touch.y1 = Math.trunc(touch.y1 / this.scale);
      touch.y2 = Math.trunc(touch.y2 / this.scale);
      return touch;
    },
  },
  components: {
    ImageSelector,
  },
};
</script>

<style scoped>
.dialog-input-box {
  width: 360px;
}
</style>