import { createRouter, createWebHistory } from 'vue-router';
import LoginView from './views/LoginView.vue';
import ChatView from './views/ChatView.vue';
import AdminSetupView from './views/AdminSetupView.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/chat',
      name: 'chat',
      component: ChatView
    },
    {
      path: '/admin-setup',
      name: 'admin-setup',
      component: AdminSetupView
    },
    {
      path: '/logout',
      name: 'logout',
      beforeEnter: (to, from, next) => {
        // Xử lý đặc biệt cho đăng xuất
        console.log("Logout route triggered");
        localStorage.clear();
        
        // Đánh dấu rõ ràng là đã đăng xuất
        sessionStorage.setItem('force_logout', 'true');
        
        next('/login');
      }
    },
    {
      path: '/',
      redirect: to => {
        // Kiểm tra nếu đã đánh dấu đăng xuất thì không tự động đăng nhập lại
        if (sessionStorage.getItem('force_logout') === 'true') {
          return '/login';
        }
        
        const username = localStorage.getItem('username');
        return username === 'admin' ? '/chat' : '/login';
      }
    }
  ]
});

// Navigation guard to protect chat route
router.beforeEach((to, from, next) => {
  // Nếu đang đi đến trang login, xóa flag force_logout
  if (to.path === '/login') {
    sessionStorage.removeItem('force_logout');
  }
  
  const username = localStorage.getItem('username');
  const forceLogout = sessionStorage.getItem('force_logout') === 'true';
  
  if (to.path === '/chat' && (!username || forceLogout)) {
    next('/login');
  } else {
    next();
  }
});

export default router; 