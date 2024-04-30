<template>
    <el-container>
        <div class = 'dialogPage-dialog'>
            <Dialog></Dialog>
        </div>
    </el-container>
</template>


<script>
import Dialog from '../components/Dialog/NewDialog'
export default {
    components:{
        Dialog
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
