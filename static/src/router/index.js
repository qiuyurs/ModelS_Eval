import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/ModelHistory',
      name: 'ModelHistory',
      component: () => import('../views/cat/modelHistory.vue'),
      meta: {
        title: '模型请求记录'
      }
    },
    {
      path: '/DatasetList',
      name: 'DatasetList',
      component: () => import('../views/cat/datasetList.vue'),
      meta: {
        title: '数据集列表'
      }
    },
    {
      path: '/addModel',
      name: 'addModel',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/add/addModel.vue'),
      meta: {
        title: '添加模型'
      }
    },{
      path: '/ModelList',
      name: 'ModelList',
      component: () => import('../views/cat/catModel.vue'),
      meta: {
        title: '大模型列表'
      }
    },{
      path: '/ModelHistory',
      name: 'ModelHistory',
      component: () => import('../views/cat/modelHistory.vue'),
      meta: {
        title: '模型请求记录'
      }
    },{
      path: '/ModelComparison',
      name: 'ModelComparison',
      component: () => import('../views/deb/ModelComparison.vue'),
      meta: {
        title: '多模型评测'
      }
    },{
      path: '/ModelComparison2',
      name: 'ModelComparison2',
      component: () => import('../views/deb/deb2.vue'),
      meta: {
        title: '模型评测'
      }
    },{
      path: '/',
      name: 'index',
      component: () => import('../views/index.vue'),
      meta: {
        title: '首页'
      }
    },
  ],
})

export default router
