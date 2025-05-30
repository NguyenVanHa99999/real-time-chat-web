<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const password = ref('');
const error = ref('');
const success = ref(false);

// Mật khẩu đơn giản để thiết lập quyền admin (trong thực tế nên sử dụng phương pháp an toàn hơn)
const ADMIN_PASSWORD = 'admin123';

function setupAdmin() {
  if (password.value === ADMIN_PASSWORD) {
    localStorage.setItem('admin_mac_verified', 'true');
    localStorage.setItem('username', 'admin');
    success.value = true;
    
    // Chuyển hướng sau 2 giây
    setTimeout(() => {
      router.push('/chat');
    }, 2000);
  } else {
    error.value = 'Mật khẩu không đúng';
  }
}
</script>

<template>
  <div class="admin-setup">
    <div class="setup-card">
      <h2>Thiết lập tài khoản Admin</h2>
      
      <div v-if="success" class="success-message">
        Thiết lập thành công! Đang chuyển hướng...
      </div>
      
      <div v-else>
        <p>Nhập mật khẩu để thiết lập máy này là admin:</p>
        
        <div class="input-group">
          <input 
            type="password" 
            v-model="password"
            placeholder="Nhập mật khẩu"
            @keyup.enter="setupAdmin"
          />
          <button @click="setupAdmin">Xác nhận</button>
        </div>
        
        <div class="error" v-if="error">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-setup {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.setup-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 420px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

h2 {
  margin-top: 0;
  color: #333;
  margin-bottom: 1.5rem;
  font-weight: 700;
  font-size: 1.8rem;
  letter-spacing: -0.5px;
}

.input-group {
  margin: 1.8rem 0;
}

input {
  width: 100%;
  padding: 1rem 1.2rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 1rem;
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
  background: linear-gradient(to right, #6e8efb, #5570c7);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(110, 142, 251, 0.2);
}

button:hover {
  background: linear-gradient(to right, #5570c7, #455fad);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(110, 142, 251, 0.3);
}

button:active {
  transform: translateY(1px);
}

.error {
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

.success-message {
  color: #4caf50;
  font-weight: bold;
  text-align: center;
  padding: 1.5rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 8px;
  margin: 1.5rem 0;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
  100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

/* Responsive adjustments */
@media (max-width: 500px) {
  .setup-card {
    padding: 2rem;
    margin: 0 1rem;
  }

  h2 {
    font-size: 1.5rem;
  }
}
</style> 