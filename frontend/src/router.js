import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    meta: { title: 'ClaimSuite' },
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/new',
    name: 'NewClaim',
    meta: { title: 'New Claim' },
    component: () => import('@/pages/NewClaim.vue'),
  },
  {
    path: '/claims',
    name: 'ClaimList',
    meta: { title: 'My Claims' },
    component: () => import('@/pages/ClaimList.vue'),
  },
  {
    path: '/claims/:name',
    name: 'ClaimDetail',
    meta: { title: 'Claim Detail', showBack: true },
    component: () => import('@/pages/ClaimDetail.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

export default router
