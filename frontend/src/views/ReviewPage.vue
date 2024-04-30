<template>
    <el-container>
        <div class = 'dialogPage-dialog'>
            <Review></Review>
        </div>
    </el-container>
</template>


<script>
import Review from '../components/Dialog/Review'
export default {
    components:{
        Review
    }
}
</script>

<style scoped>
.dialogPage-dialog {
    height: 80vh;
    width: 100vw;
    padding: 50px;
}
</style>
