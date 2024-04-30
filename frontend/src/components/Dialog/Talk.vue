<template>
  <UserTalk
    @inputFocus="handleFocus"
    @editTurn="handleEdit"
    v-if="data.isUser"
    :data="data"
    :index="index"
    :selected="selected"
  ></UserTalk>
  <SysTalk
    @inputFocus="handleFocus"
    @editTurn="handleEdit"
    v-else
    :data="data"
    :index="index"
    :selected="selected"
  ></SysTalk>
</template>

<script>
import SysTalk from "./SysTalk";
import UserTalk from "./UserTalk";

export default {
  props: ["data", "index", "selected"],
  components: {
    SysTalk,
    UserTalk,
  },
  data() {
    return {};
  },
  methods: {
    handleFocus(focus) {
      console.log("focus", focus);
      this.$emit("inputFocus", focus);
    },
    handleEdit(index, text) {
      console.log("edit turn", index, text);
      this.$emit("editTurn", index, text);
    },
  },
};
</script>


<style scoped>
</style>
