import Vue from 'vue'
import Router from 'vue-router'
import Base from './views/Base.vue'
import DialogPage from './views/DialogPage'
import NewDialogPage from './views/NewDialogPage'
import ReviewPage from './views/ReviewPage'

Vue.use(Router)

export default new Router({
    routes: [{
        path: '/',
        name: 'Base',
        component: Base,
        children: [
            {
                path: '/dialog',
                name: 'DialogPage',
                component: DialogPage
            }, {
                path: 'review',
                name: 'ReviewPage',
                component: ReviewPage
            },{
                path: 'new',
                name: 'NewDialogPage',
                component: NewDialogPage
            }]
    }]
})