<template>
  <el-image
      :src="image"
      :fit="fit"
      :preview-src-list="image-list"></el-image>
</template>

<script>
export default {
  name: "Image",
  props:["image", "image-list"],
  data() {
    return {
      fit: "fill"
    };
  },
  mounted: function () {
  },
  methods: {
      
  },
};
</script>

<style>
</style>