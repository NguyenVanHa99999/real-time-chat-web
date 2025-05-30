<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const error = ref('');
const loading = ref(false);
const isMacDevice = ref(false);

// Kiểm tra xem có phải thiết bị Mac không
onMounted(() => {
  const userAgent = navigator.userAgent.toLowerCase();
  isMacDevice.value = userAgent.includes('macintosh') && !userAgent.includes('windows');
});

const login = async () => {
  if (!username.value.trim()) {
    error.value = 'Username is required';
    return;
  }
  
  // Xóa tất cả trạng thái đăng xuất trước khi đăng nhập
  localStorage.removeItem('logged_out');
  sessionStorage.removeItem('force_logout');
  sessionStorage.removeItem('admin_logged_out');
  
  loading.value = true;
  error.value = '';
  
  try {
    console.log('Sending login request for:', username.value);
    
    // Tạo FormData thay vì JSON
    const formData = new FormData();
    formData.append('username', username.value);
    
    const response = await fetch('http://192.168.1.5:8000/login', {
      method: 'POST',
      body: formData
    });
    
    console.log('Response status:', response.status);
    const data = await response.json();
    console.log('Response data:', data);
    
    if (response.ok) {
      localStorage.setItem('username', username.value);
      // Đảm bảo xóa tất cả flag đăng xuất
      localStorage.removeItem('logged_out');
      sessionStorage.removeItem('force_logout');
      sessionStorage.removeItem('admin_logged_out');
      router.push('/chat');
    } else {
      error.value = data.message || 'Login failed';
    }
  } catch (err) {
    console.error('Login error:', err);
    error.value = 'Error connecting to server';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Welcome to Chat App</h1>
      <div class="input-group">
        <input 
          type="text" 
          v-model="username" 
          placeholder="Enter your username"
          @keyup.enter="login"
          :disabled="loading"
        />
      </div>
      <button @click="login" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
      <div class="error-message" v-if="error">{{ error }}</div>
      
      <!-- Hiển thị liên kết thiết lập admin nếu đang sử dụng máy Mac -->
      <div class="admin-link" v-if="isMacDevice">
        <p>Sử dụng máy Mac?</p>
        <router-link to="/admin-setup">Thiết lập máy này là Admin</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 420px;
  text-align: center;
  transform: translateY(0);
  transition: transform 0.3s, box-shadow 0.3s;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-box:hover {
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  transform: translateY(-5px);
}

h1 {
  margin-bottom: 2rem;
  color: #333;
  font-weight: 700;
  font-size: 2.2rem;
  letter-spacing: -0.5px;
}

.input-group {
  margin-bottom: 1.8rem;
}

input {
  width: 100%;
  padding: 1rem 1.2rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

input:focus {
  outline: none;
  border-color: #6e8efb;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(110, 142, 251, 0.15);
}

button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(to right, #4caf50, #45a049);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(76, 175, 80, 0.2);
}

button:hover {
  background: linear-gradient(to right, #43a047, #388e3c);
  box-shadow: 0 6px 15px rgba(76, 175, 80, 0.3);
  transform: translateY(-2px);
}

button:active {
  transform: translateY(1px);
}

button:disabled {
  background: linear-gradient(to right, #cccccc, #bbbbbb);
  box-shadow: none;
  cursor: not-allowed;
  transform: none;
  opacity: 0.7;
}

.error-message {
  color: #f44336;
  margin-top: 1.2rem;
  background: rgba(244, 67, 54, 0.08);
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%, 60% { transform: translateX(-5px); }
  40%, 80% { transform: translateX(5px); }
}

.admin-link {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.admin-link p {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.admin-link a {
  color: #6e8efb;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
  position: relative;
}

.admin-link a:hover {
  color: #5570c7;
}

.admin-link a::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -3px;
  left: 0;
  background-color: #6e8efb;
  transition: width 0.3s;
}

.admin-link a:hover::after {
  width: 100%;
}

/* Responsive adjustments */
@media (max-width: 500px) {
  .login-box {
    padding: 2rem;
    margin: 0 1rem;
  }

  h1 {
    font-size: 1.8rem;
  }
}
</style> 