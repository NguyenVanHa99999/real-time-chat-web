<script setup>
import { onMounted, watch, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// CHỨC NĂNG MỚI: Kiểm tra xem đã đăng xuất chưa ngay khi tải trang
if (sessionStorage.getItem('force_logout') === 'true' || 
    localStorage.getItem('logged_out') === 'true' ||
    sessionStorage.getItem('admin_logged_out') === 'true') {
  console.log('Previous logout detected, clearing all storage');
  localStorage.clear();
  // Giữ lại flag đăng xuất trong sessionStorage
}

// Flag để theo dõi người dùng đã đăng xuất
const userLoggedOut = ref(sessionStorage.getItem('force_logout') === 'true' || 
                         localStorage.getItem('logged_out') === 'true' ||
                         sessionStorage.getItem('admin_logged_out') === 'true');

// Địa chỉ IP của máy Mac admin
const MAC_IP = '172.20.10.2';

// Hàm để kiểm tra xem có phải máy Mac hay không dựa vào UserAgent
function isMacDevice() {
  const userAgent = navigator.userAgent.toLowerCase();
  return userAgent.includes('macintosh') && !userAgent.includes('windows');
}

// Xác định nếu đây là máy chủ Mac chính
function isMacServer() {
  // Nếu đang chạy trên máy Mac (IP = MAC_IP)
  return window.location.hostname === 'localhost' || 
         window.location.hostname === MAC_IP;
}

// Thêm tham số "admin=true" vào URL để admin có thể đăng nhập từ máy Mac
function hasAdminParam() {
  return new URLSearchParams(window.location.search).get('admin') === 'true';
}

// Theo dõi localStorage để phát hiện đăng xuất
window.addEventListener('storage', (event) => {
  if (event.key === 'username' && event.newValue === null) {
    userLoggedOut.value = true;
    localStorage.setItem('logged_out', 'true');
  }
});

onMounted(() => {
  // TĂNG CƯỜNG KIỂM TRA: Ngăn chặn tự động đăng nhập sau khi đăng xuất
  if (userLoggedOut.value || 
      sessionStorage.getItem('force_logout') === 'true' ||
      sessionStorage.getItem('admin_logged_out') === 'true') {
    console.log('User previously logged out, preventing auto-login');
    // Đảm bảo xóa tất cả thông tin đăng nhập
    localStorage.removeItem('username');
    localStorage.removeItem('admin_mac_verified');
    
    // Chuyển hướng về trang đăng nhập nếu đang ở trang khác
    if (router.currentRoute.value.path !== '/login') {
      router.push('/login');
    }
    return;
  }
  
  // Flag xác định đây là máy Mac admin
  const adminFlag = localStorage.getItem('admin_mac_verified');
  
  // Nếu máy Mac đang chạy server
  if (isMacDevice() && (isMacServer() || hasAdminParam())) {
    localStorage.setItem('admin_mac_verified', 'true');
    localStorage.setItem('username', 'admin');
    router.push('/chat');
    console.log('Admin Mac verified and logged in automatically');
  }
  // Duy trì phiên đăng nhập cho admin đã xác thực
  else if (adminFlag === 'true' && isMacDevice()) {
    localStorage.setItem('username', 'admin');
    router.push('/chat');
    console.log('Admin Mac session continued');
  }
  // Nếu là máy khác truy cập từ URL chứa IP của máy Mac
  else if (window.location.hostname === MAC_IP && !isMacDevice()) {
    // Đảm bảo xóa trạng thái admin nếu không phải máy Mac
    if (localStorage.getItem('username') === 'admin') {
      localStorage.removeItem('username');
      localStorage.removeItem('admin_mac_verified');
      console.log('Non-Mac device accessing via Mac IP, admin status cleared');
    }
  }
});

// Xóa flag logged_out khi người dùng đăng nhập lại
watch(() => router.currentRoute.value.path, (newPath) => {
  if (newPath === '/login') {
    // Chỉ xóa flag đăng xuất khi là thao tác chủ động của người dùng
    // (click vào form đăng nhập), không phải khi bị chuyển hướng
    const handleFormClick = () => {
      localStorage.removeItem('logged_out');
      sessionStorage.removeItem('force_logout');
      sessionStorage.removeItem('admin_logged_out');
      userLoggedOut.value = false;
      
      // Cleanup event listener
      setTimeout(() => {
        const loginForm = document.querySelector('.login-container');
        if (loginForm) {
          loginForm.removeEventListener('click', handleFormClick);
        }
      }, 500);
    };
    
    // Thêm event listener khi người dùng tương tác với form
    setTimeout(() => {
      const loginForm = document.querySelector('.login-container');
      if (loginForm) {
        loginForm.addEventListener('click', handleFormClick);
      }
    }, 500);
  }
}, { immediate: true });
</script>

<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
}

.app-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}
</style>
