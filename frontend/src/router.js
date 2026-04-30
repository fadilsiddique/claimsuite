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
    path: '/insights',
    name: 'Insights',
    meta: { title: 'Insights' },
    component: () => import('@/pages/Insights.vue'),
  },
  {
    path: '/claims/:name',
    name: 'ClaimDetail',
    meta: { title: 'Claim Detail', showBack: true },
    component: () => import('@/pages/ClaimDetail.vue'),
  },
  {
    path: '/claims/:name/edit',
    name: 'EditClaim',
    meta: { title: 'Edit Claim', showBack: true },
    component: () => import('@/pages/NewClaim.vue'),
  },
]

let router = createRouter({
  history: createWebHistory('/frontend'),
  routes,
})

export default router
