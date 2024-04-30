export default {
    namespaced: true,
    state: {
        session: '',
        isLogin:localStorage['usn']?true:false,
        user:localStorage['usn'] || '',
        user_id:localStorage['user_id'] || '',
        token:localStorage['token'] || ''
    },
    mutations: {
        setSession(state, session) {
            state.session = session;
        },
        setUser(state, user){
            state.user = user;
            state.user_id = user['user_id'];
            state.token = user['token'];
            state.isLogin = true;

            localStorage['usn'] = user['usn'];
            localStorage['user_id'] = user['user_id'];
            localStorage['token'] = user['token'];
        },
        exitUser(state){
            state.user = '';
            state.user_id = '';
            state.token = '';
            state.isLogin = false;
            
            localStorage['usn'] = '';
            localStorage['user_id'] = '';
            localStorage['token'] = '';
        }
    }
}