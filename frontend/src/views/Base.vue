<template>
    <el-container class='base-container'>
        <el-header :height='"50x"' class="base-header">
            <el-row>
                <el-col class='nav-item' :span='18' ><a>IPA对话系统</a></el-col>
                <!-- <el-col class='nav-item' :span='2' @click.native="changeTab('dialog')" ><a>对话展示</a></el-col>
                <el-col class='nav-item' :span='2' @click.native="changeTab('list')"><a>控制台</a></el-col>
                <el-col class='nav-item' :span='2' @click.native="changeTab('login')" v-if="!isLogin"><a>登录</a></el-col>
                <el-col class='nav-item' :span='2' v-if="isLogin">
                    <el-dropdown>
                        <span class="usn">
                            {{usn}}<i class="el-icon-arrow-down el-icon--right"></i>
                        </span>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item @click.native="exitLogin">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </el-dropdown>
                </el-col> -->
            </el-row>
        </el-header>
        <el-main class="base-main">  
            <router-view @exitLogin = "exitLogin"/>        
        </el-main>
    </el-container>
</template>


<script>
export default {
    name:'Base',
    data(){
        return {
            isLogin:false,
            usn:''
        }
    },
    methods:{
        autoLogin:function(){
            let usn = localStorage['usn'];
            if (usn || this.$store.state.user.isLogin){
                this.isLogin = true;
                this.usn = usn || this.$store.state.user.user;
            } else {
                this.isLogin = false;
                this.usn = '';
            }
        },
        exitLogin:function(){
            this.$store.commit('user/exitUser');
            this.isLogin = false;
            this.usn = '';
            this.$router.replace('/dialog')
        },
        changeTab: function(target) {
            if (target == 'login'){
                this.$router.replace('/login');
            } else if (target == 'list'){
                if (!this.$store.state.user.isLogin){
                    this.$router.replace('/login');
                    return;
                }
                this.$router.replace('/list')
            } else if (target == 'dialog'){
                this.$router.replace('/dialog')
            }
        }
    },
    mounted:function(){
        // this.autoLogin();
        // if (!this.isLogin){
        //         this.$router.replace('/dialog')
        // }
    },
    beforeUpdate:function(){
        this.autoLogin();
    }

}
</script>

<style scoped>
.base-header {
    background-color: rgb(0, 21, 41);
    color: white;
    line-height: 40px;
    font-size: 22px;
    height: 6vh;
}
.base-container {
    background-image: url('../assets/bg.png');
    background-repeat: no-repeat;
    background-size: 100% 100%;
    height: 100vh;
    padding: 0;
}

.base-main {
    height: 100%;
    width: 100%;
    padding: 0;
}
.usn {
    color:white;
    font-size: 22px;
}
.nav-item {
    cursor: pointer;
}
</style>
