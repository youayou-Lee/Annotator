import { createRouter, createWebHistory } from 'vue-router'
import AnnotatorView from '../views/AnnotatorView.vue'
import AdminView from '../views/AdminView.vue'
import FormatUploader from '../components/FormatUploader.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/admin'
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    },
    {
      path: '/annotator/:taskId',
      name: 'annotator',
      component: AnnotatorView,
      props: true
    },
    {
      path: '/format',
      name: 'format',
      component: FormatUploader
    }
  ]
})

export default router