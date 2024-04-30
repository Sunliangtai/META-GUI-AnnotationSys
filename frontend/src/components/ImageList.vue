<template>
  <div :class="container_class" id="image-container">
    <h2>截图列表</h2>
    <div
      v-for="(item, index) in image_list"
      :key="index"
      class="image-item"
      :class="{ highlight: selected_index == index }"
    >
      <el-row type="flex" justify="center">
        <el-col :span="bigger ? 11 : 9"
          ><el-image
            :style="image_style"
            :src="item.from"
            fit="fill"
            :preview-src-list="[item.from]"
          ></el-image
        ></el-col>
        <el-col :span="bigger ? 4 : 4">
          <el-tooltip
            effect="dark"
            :content="item.note"
            placement="bottom"
            :disabled="item.note == ''"
          >
            <el-tag class="operation">{{
              item.operation == "" ? "等待操作" : item.operation
            }}</el-tag>
          </el-tooltip>
        </el-col>
        <el-col :span="bigger ? 11 : 9"
          ><el-image
            v-if="item.to"
            :style="image_style"
            :src="item.to"
            fit="fill"
            :preview-src-list="[item.to]"
          >
          </el-image
        ></el-col>
      </el-row>
      <el-button type="primary" size="small" @click="select(index)"
        >从下方插入<i class="el-icon-refresh"></i
      ></el-button>
      <el-button type="danger" size="small" @click="delete_image(index)"
        >删除<i class="el-icon-refresh"></i
      ></el-button>
    </div>
  </div>
</template>

<script>
function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

export default {
  name: "ImageList",
  props: ["bigger"],
  data() {
    return {
      image_list: [],
      selected_index: -1,
    };
  },
  // updated: function () {
  //   let body = document.getElementById("image-container");
  //   body.scrollTop = body.scrollHeight;
  // },
  methods: {
    async update_click(image, position) {
      let img_obj = new Image();
      let canvas = document.createElement("canvas");
      img_obj.src = image;
      while (img_obj.width == 0) await sleep(100);
      canvas.height = img_obj.height;
      canvas.width = img_obj.width;
      let ctx = canvas.getContext("2d");
      ctx.drawImage(img_obj, 0, 0);
      ctx.strokeStyle = "red";
      let width = 10;
      let scale = 0.25;
      ctx.strokeRect(
        position.x1 * scale - width / 2,
        position.y1 * scale - width / 2,
        width,
        width
      );
      return canvas.toDataURL("image/png");
    },
    async update_read(image, box) {
      let img_obj = new Image();
      img_obj.src = image;
      while (img_obj.width == 0) await sleep(100);
      let canvas = document.createElement("canvas");
      canvas.height = img_obj.height;
      canvas.width = img_obj.width;
      let ctx = canvas.getContext("2d");
      ctx.drawImage(img_obj, 0, 0);
      ctx.strokeStyle = "red";
      let scale = 0.25;
      ctx.strokeRect(
        box.left * scale,
        box.top * scale,
        box.width * scale,
        box.height * scale
      );
      return canvas.toDataURL("image/png");
    },
    async add_image(image, image_id, operation, note, touch) {
      // console.log("add image", image_id);
      if (this.selected_index != -1) {
        // console.log("update last");
        let last_item = this.image_list[this.selected_index];
        let index = this.selected_index;
        if (operation == "点击")
          last_item.from = await this.update_click(last_item.from, touch);
        else if (operation == "读取")
          last_item.from = await this.update_read(last_item.from, touch);
        last_item.to = image;
        last_item.operation = operation;
        last_item.note = note;
        this.image_list.splice(index, 1, last_item);
        // console.log("last", last_item, index);
      }
      let index = this.selected_index+1;
      this.selected_index = index;
      let item = {
        from: image,
        to: "",
        operation: "",
        note: "",
        image_id: image_id,
      };
      // console.log("new", item);
      this.image_list.splice(index, 0, item);
      return 1;
    },
    select(index) {
      this.selected_index = index;
    },
    delete_image(index) {
      this.image_list.splice(index, 1);
      if (this.selected_index >= this.image_list.length)
        this.selected_index = this.image_list.length - 1;
    },
    clear_image() {
      this.image_list = [];
      this.selected_index = -1;
    },
    replace_image(new_image) {
      this.image_list = new_image;
    },
    get_saved_image() {
      let res = [];
      for (let i = 0; i < this.image_list.length; i++)
        res.push(this.image_list[i].image_id);
      return res;
    },
  },
  computed: {
    container_class() {
      if (this.bigger) {
        return "image-container-bigger";
      } else return "image-container";
    },
    image_style() {
      if (this.bigger) {
        return {
          width: "320px",
          height: "560px",
          marginBottom: "5px",
        };
      } else
        return {
          width: "98px",
          height: "170px",
          marginBottom: "5px",
        };
    },
  },
};
</script>

<style>
.image-container {
  overflow: auto;
  width: 290px;
  height: 650px;
}

.image-container-bigger {
  overflow: auto;
  width: 800px;
  height: 650px;
}
.image-item {
  margin-bottom: 5px;
}
.highlight {
  border: 2px solid #67c23a;
}
.operation {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>