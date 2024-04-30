<template>
    <div class='login'>
        <div class="login-header">
            <el-tabs type="border-card">
            <el-tab-pane label="登录" class="login-pane">
                <el-input class='input-box' v-model="usn" placeholder="用户名" clearable></el-input>
                <el-input class='input-box' v-model="password" placeholder="密码" type="password" clearable></el-input>
                <div class="login-buttons">
                    <el-button type='success' @click="login">登录</el-button>
                </div>
            </el-tab-pane>
            <el-tab-pane label="注册">
                <el-input class='input-box' v-model="register_usn" placeholder="用户名" clearable></el-input>
                <el-input class='input-box' v-model="register_pw" placeholder="密码" type="password" clearable></el-input>
                 <el-input class='input-box' v-model="register_pw2" placeholder="重复输入密码" type="password" clearable></el-input>
                <div class="login-buttons">
                    <el-button type='success' @click="register">注册</el-button>
                </div>
            </el-tab-pane>
         </el-tabs>
        </div>
    </div>
</template>

<script>
import { Message } from 'element-ui';
import {net_login,net_register} from '@/network'

export default {
    name:"Login",
    data(){
        return {
            usn:'',
            password:'',
            register_usn:'',
            register_pw:'',
            register_pw2:''
        }
    },
    methods:{
        login:async function(){
            
            let usn = this.usn;
            let password = this.password;
            if (!usn){
                Message.error("请输入用户名");
                return;
            }
            if (!password){
                Message.error("请输入密码");
                return;
            }
            let res = await net_login({'usn':usn,'password':password});
            // let res = {'status':1}
            if (res['status']==1){
                res['usn'] = usn;
                this.$store.commit('user/setUser',res);
                this.$router.replace('/dialog');
            } else if (res['status'] == -1){
                this.$message.error("密码错误");
            } else {
                this.$message.error("登录失败，请联系管理员");
            }
        },
        register:async function(){
            let usn = this.register_usn;
            let password = this.register_pw;
            let password2 = this.register_pw2;
            if (!usn){
                Message.error("请输入用户名");
                return;
            }
            if (!password || !password2){
                Message.error("请输入密码");
                return;
            }
            if (password!=password2){
                Message.error("两次输入的密码不一致");
                return ;
            }
            let res = await net_register({'usn':usn,'password':password})
            // let res = {'status':1}
            if (res['status']==1){
                // login
                let data = {'usn':usn,'password':password};
                let res = await net_login(data);
                if (res['status'] == 1){
                    res['usn'] = usn;
                    this.$store.commit('user/setUser',res);
                    this.$router.replace('/dialog');
                }
            } else if (res['status'] == -1){
                this.$message.error("用户名已被占用");
            } else {
                this.$message.error("注册失败，请联系管理员");
            }
        }
    },
    beforeMount: function(){
        if (this.$store.state.user.isLogin){
            this.$router.replace('/dialog')
        }
    }
}
</script>

<style scoped>
.login {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 600px;
    flex-direction: column;
}

.login-header {
    width:400px;
}

.main {
    width: 400px;
    height: 100%;
    background-color: white;
}

.input-box{
    margin-bottom: 10px;
}

.login-buttons {
    display: flex;
   flex-direction: row-reverse;
}

</style>
