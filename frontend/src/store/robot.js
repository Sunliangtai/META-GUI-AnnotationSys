export default {
    namespaced: true,
    state: {
        current_robot:localStorage['current_robot']?JSON.parse(localStorage['current_robot']):{}
    },
    mutations: {
        set_robot(state, current_robot) {
            state.current_robot = current_robot;
            localStorage['current_robot'] = JSON.stringify(current_robot);
        },
        edit_robot(state,robot) {
            state.current_robot = robot;
            localStorage['current_robot'] = JSON.stringify(robot);
        }
    }
}