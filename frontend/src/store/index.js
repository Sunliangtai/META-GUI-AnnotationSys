import Vue from 'vue';
import Vuex from 'vuex';
import user from './user';
import robot from './robot'

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        user,
        robot
    },
});