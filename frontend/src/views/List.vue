<template>
    <el-container class='list-view'>
        <div class="robot-list">
            <RobotCard v-for="(item,i) in robots" :key="i" :robot="item" @click.native="edit_app(i)" @delete_app="delete_app"></RobotCard>
            <el-card class="card add_card" shadow="never" :body-style="{'padding':0}">
                <div class="add-button" @click="dialog_visible = !dialog_visible">+</div>
            </el-card>
        </div>
    <el-dialog
        title="添加新机器人"
        :visible.sync="dialog_visible"
        width="30%"
        @closed="handleClose">
        <span>
            <el-input v-model="new_robot" placeholder="请输入新机器人的名字" clearable></el-input>
        </span>
        <span slot="footer" class="dialog-footer">
            <el-button @click="dialog_visible = false">取 消</el-button>
            <el-button type="primary" @click="add_app">确 定</el-button>
        </span>
    </el-dialog>

    </el-container>
</template>


<script>
import {net_get_robot_list,net_delete_robot,net_add_robot} from '@/network'
import RobotCard from '../components/robot/RobotCard'

export default {
    name:"List",
    data(){
        return {
            robots:[],
            dialog_visible:false,
            new_robot:""
        }
    },
    mounted:async function (){
        let data = await net_get_robot_list({'user_id':this.$store.state.user.user_id,'token':this.$store.state.user.token});
        if (data['status'] == 1){
            this.robots = data['app_list'];
        } else if (data['status'] == -2){
            this.$emit('exitUser');
        }
    },
    components:{
        RobotCard
    },
    methods:{
        delete_app:async function (app){   
            let data = {'user_id':this.$store.state.user.user_id,'token':this.$store.state.user.token,
            'app_id':app['app_id']};
            let res = await net_delete_robot(data);
            if (res['status'] == 1){
                for (let i=0;i<this.robots.length;i++){
                    let item = this.robots[i];
                    if (item['app_id'] == app['app_id']){
                        this.robots.splice(i,1);
                        break;
                    }
                }
            } else {
                this.$message.error("删除失败");
            }
        },
        add_app:async function (){
            let name = this.new_robot;
            if (!name){
                this.$message.error("请输入新机器人的名字！");
                return;
            }
            this.dialog_visible = false;

            let data = {'user_id':this.$store.state.user.user_id,'token':this.$store.state.user.token,
            'app_name':name};
            let res = await net_add_robot(data);
            if (res['status'] == 1){
                this.robots.push({'app_name':name,'app_id':res['app_id']});
            } else {
                this.$message.error("添加失败");
            }
        },
        handleClose:function (){
            this.new_robot = "";
        },
        edit_app:function (i){
            this.$store.commit('robot/set_robot',this.robots[i]);
            this.$router.replace('/panel')
        }
    }
}
</script>


<style>
.list-view {
    background-color: rgb(249,249,249);
    height: 100%;
    width: 100%;
}

.robot-list {
    padding-top: 40px;
    padding-left: 40px;
    display: flex;
    flex-wrap: wrap;
}

.card {
  padding: 0;
  height: 300px;
  width: 186px;
  display: flex;
  margin-right: 10px;
}

.add-button {
    font-size: 100px;
    line-height: 298px;
    text-align: center;
    width: 184px;
    color: rgb(0,134,209);
    border: 1px dashed rgb(0,134,209);
}

.add-button:hover{
    cursor: pointer;
}


</style>
