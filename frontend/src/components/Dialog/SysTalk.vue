<template>
  <div class="talk-box">
    <span class="el-icon-user-solid avatar"></span>
    <div v-if="!enable_edit" class="text-box" :class="{border: selected}" @dblclick="handleEdit">
      <el-popover
        placement="bottom"
        title="参考翻译:"
        width="300"
        trigger="hover"
        :content="data.program"
      >
        <div slot="reference" class="text-box">{{ data.text }}</div>
      </el-popover>
    </div>
    <el-input v-else autofocus v-model="input" @blur="handleBlur"></el-input>
  </div>
</template>

<script>
export default {
  props: ["data", "index","selected"],
  data() {
    return {
      url: "",
      enable_edit: false,
      input:""
    };
  },
  methods: {
    handleEdit() {
      this.input = this.data.text;
      this.enable_edit = true;
      this.$emit("inputFocus", true);
    },
    handleBlur() {
      this.enable_edit = false;
      this.$emit("inputFocus", false);
      this.$emit("editTurn", this.index, this.input);
    },
  },
  computed: {
    table: function () {
      return this.data.table;
    },
    colName: function () {
      if (this.data.colName) return this.data.colName;
      let colName = {};
      for (let col in this.data.table[0]) colName[col] = col;
      return colName;
    },
  },
};
</script>

<style scoped>
.border {
  border: black 2px solid;
}

.talk-table {
  width: 60%;
}
.talk-box {
  display: flex;
  justify-content: flex-start;
  margin-top: 10px;
  padding-left: 20px;
}
.text-box {
  background-color: rgb(246, 246, 246);
  min-height: 40px;
  max-width: 540px;
  border-radius: 15px;
  font-size: 20px;
  line-height: 40px;
  padding-left: 5px;
  display: inline-block;
  margin: 5px;
  padding: 0 15px;
}
.avatar {
  display: inline-block;
  height: 40px;
  width: 40px;
  border-radius: 20px;
  font-size: 30px;
  background-color: rgb(192, 196, 204);
  line-height: 40px;
  color: white;
  text-align: center;
  margin: 5px;
}
</style>
