<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  username: {
    type: String,
    required: true
  }
});

const users = ref([]);
const messages = ref([]);
const newMessage = ref('');
const selectedUser = ref(null);
const socket = ref(null);
const error = ref('');

// Fetch online users
const fetchUsers = async () => {
  try {
    const response = await fetch('http://192.168.1.5:8000/users');
    if (response.ok) {
      const data = await response.json();
      // Filter out current user
      users.value = data.users.filter(user => user !== props.username);
    } else {
      error.value = 'Failed to load users';
    }
  } catch (err) {
    error.value = 'Error connecting to server';
    console.error(err);
  }
};

// Connect to WebSocket
const connectWebSocket = () => {
  if (socket.value) {
    socket.value.close();
  }
  
  socket.value = new WebSocket(`ws://192.168.1.5:8000/ws/${props.username}`);
  
  socket.value.onopen = () => {
    console.log('WebSocket connected');
    error.value = '';
  };
  
  socket.value.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      
      // Xử lý thông báo hệ thống
      if (data.system) {
        messages.value.push({
          system: true,
          message: data.message,
          timestamp: new Date().toLocaleTimeString()
        });
        
        // Cập nhật danh sách người dùng khi có thay đổi trạng thái
        fetchUsers();
        return;
      }
      
      // Xử lý thông báo lỗi
      if (data.error) {
        error.value = data.message;
        return;
      }
      
      // Xử lý tin nhắn thông thường
      messages.value.push({
        from: data.from || 'Server',
        message: data.message,
        timestamp: new Date().toLocaleTimeString()
      });
    } catch (err) {
      console.error('Error parsing message', err);
    }
  };
  
  socket.value.onerror = (event) => {
    error.value = 'WebSocket error occurred';
    console.error('WebSocket error:', event);
  };
  
  socket.value.onclose = () => {
    console.log('WebSocket connection closed');
  };
};

// Send message
const sendMessage = () => {
  if (!selectedUser.value || !newMessage.value.trim() || !socket.value || socket.value.readyState !== WebSocket.OPEN) {
    return;
  }
  
  const message = {
    to: selectedUser.value,
    message: newMessage.value
  };
  
  socket.value.send(JSON.stringify(message));
  
  // Add to local messages
  messages.value.push({
    from: props.username,
    to: selectedUser.value,
    message: newMessage.value,
    timestamp: new Date().toLocaleTimeString()
  });
  
  newMessage.value = '';
};

// Select user to chat with
const selectUser = (user) => {
  selectedUser.value = user;
  // Clear message history when changing users
  messages.value = [];
};

// Logout function
const logout = async () => {
  try {
    // Đóng WebSocket nếu đang mở
    if (socket.value && socket.value.readyState === WebSocket.OPEN) {
      socket.value.close();
    }
    
    // Xử lý đặc biệt cho tài khoản admin
    const isAdmin = props.username === 'admin';
    
    // Nếu không phải admin, thông báo cho server về việc đăng xuất
    if (!isAdmin) {
      try {
        await fetch('http://192.168.1.5:8000/logout', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username: props.username })
        });
      } catch (apiErr) {
        console.error('API logout error (continuing):', apiErr);
      }
    }
    
    // Đảm bảo xóa sạch dữ liệu
    localStorage.clear();
    sessionStorage.setItem('force_logout', 'true');
    
    // Xóa bỏ các flag đặc biệt của admin
    if (isAdmin) {
      localStorage.removeItem('admin_mac_verified');
      sessionStorage.setItem('admin_logged_out', 'true');
    }
    
    console.log('Logout successful, redirecting to login page...');
    
    // Sử dụng đường dẫn tuyệt đối
    const currentOrigin = window.location.origin;
    window.location.href = `${currentOrigin}/login`;
  } catch (err) {
    console.error('Error during logout:', err);
    
    // Đảm bảo xóa sạch dữ liệu ngay cả khi có lỗi
    localStorage.clear();
    sessionStorage.setItem('force_logout', 'true');
    
    const currentOrigin = window.location.origin;
    window.location.href = `${currentOrigin}/login`;
  }
};

// Watch for selected user changes and poll for users regularly
watch(selectedUser, () => {
  messages.value = [];
});

onMounted(() => {
  fetchUsers();
  connectWebSocket();
  
  // Poll for users every 10 seconds
  const interval = setInterval(fetchUsers, 10000);
  
  return () => {
    clearInterval(interval);
  };
});

onUnmounted(() => {
  if (socket.value) {
    socket.value.close();
  }
});
</script>

<template>
  <div class="chat-container">
    <div class="sidebar">
      <div class="user-info">
        <h3>{{ username }}</h3>
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
      <div class="users-list">
        <h4>Online Users</h4>
        <ul>
          <li 
            v-for="user in users" 
            :key="user"
            @click="selectUser(user)"
            :class="{ active: selectedUser === user }"
          >
            {{ user }}
          </li>
        </ul>
        <div v-if="users.length === 0" class="no-users">No users online</div>
      </div>
    </div>
    
    <div class="chat-main">
      <div class="chat-header" v-if="selectedUser">
        <h3>Chat with {{ selectedUser }}</h3>
      </div>
      <div class="chat-header" v-else>
        <h3>Select a user to start chatting</h3>
      </div>
      
      <div class="messages-container">
        <div v-if="!selectedUser" class="select-user-message">
          Select a user from the sidebar to start a conversation
        </div>
        
        <div v-else-if="messages.length === 0" class="no-messages">
          No messages yet. Start the conversation!
        </div>
        
        <div v-else class="messages">
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            :class="[
              'message', 
              msg.system ? 'system' : (msg.from === username ? 'sent' : 'received')
            ]"
          >
            <div class="message-content">
              <p>{{ msg.message }}</p>
              <span class="timestamp">{{ msg.timestamp }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="message-input" v-if="selectedUser">
        <input 
          type="text" 
          v-model="newMessage" 
          placeholder="Type a message..." 
          @keyup.enter="sendMessage"
        />
        <button @click="sendMessage">Send</button>
      </div>
      
      <div class="error-banner" v-if="error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 100%;
  min-height: 600px;
}

.sidebar {
  width: 300px;
  background-color: #f5f5f7;
  border-right: 1px solid #e1e1e3;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
  transition: width 0.3s;
}

.user-info {
  padding: 20px;
  border-bottom: 1px solid #e1e1e3;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
}

.user-info h3 {
  margin: 0;
  font-weight: 600;
  font-size: 1.3rem;
  color: #000;
}

.logout-btn {
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.2);
  color: #000;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.logout-btn:active {
  transform: translateY(0);
}

.users-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.users-list h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #000;
  font-weight: 600;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.users-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.users-list li {
  padding: 15px 20px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  color: #000;
  font-size: 1.1rem;
}

.users-list li::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #4caf50;
  border-radius: 50%;
  margin-right: 10px;
}

.users-list li:hover {
  background-color: #e9e9ec;
}

.users-list li.active {
  background-color: #e1e5ff;
  color: #000;
  font-weight: 500;
}

.no-users {
  color: #000;
  text-align: center;
  margin-top: 30px;
  font-style: italic;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

.chat-header {
  padding: 18px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e1e1e3;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 1;
}

.chat-header h3 {
  margin: 0;
  font-weight: 600;
  color: #000;
  font-size: 1.3rem;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f9f9fc;
}

.select-user-message, .no-messages {
  display: flex;
  height: 100%;
  justify-content: center;
  align-items: center;
  color: #000;
  font-size: 1.1rem;
}

.messages {
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 16px;
  max-width: 75%;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.sent {
  align-self: flex-end;
}

.message.received {
  align-self: flex-start;
}

.message-content {
  padding: 15px 20px;
  border-radius: 18px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-size: 1.1rem;
}

.sent .message-content {
  background: linear-gradient(135deg, #6e8efb 0%, #5570c7 100%);
  color: #000;
  border-bottom-right-radius: 4px;
}

.received .message-content {
  background-color: #fff;
  border-bottom-left-radius: 4px;
  color: #000;
}

.system {
  align-self: center;
  max-width: 85%;
}

.system .message-content {
  background-color: #f1f1f3;
  color: #000;
  font-style: italic;
  padding: 8px 16px;
  border-radius: 15px;
  font-size: 0.9rem;
}

.message p {
  margin: 0;
  line-height: 1.5;
  font-size: 1.1rem;
}

.timestamp {
  display: block;
  font-size: 0.85rem;
  margin-top: 5px;
  text-align: right;
}

.sent .timestamp {
  color: #000;
}

.received .timestamp {
  color: #000;
}

.message-input {
  display: flex;
  padding: 15px 20px;
  border-top: 1px solid #e1e1e3;
  background-color: #fff;
}

.message-input input {
  flex: 1;
  padding: 15px 20px;
  border: 1px solid #ddd;
  border-radius: 24px;
  font-size: 1.1rem;
  transition: all 0.3s;
}

.message-input input:focus {
  outline: none;
  border-color: #6e8efb;
  box-shadow: 0 0 0 2px rgba(110, 142, 251, 0.1);
}

.message-input button {
  padding: 0 25px;
  margin-left: 10px;
  background: linear-gradient(to right, #6e8efb, #5570c7);
  color: white;
  border: none;
  border-radius: 24px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
  height: 50px;
}

.message-input button:hover {
  transform: translateY(-2px);
  box-shadow: 0 3px 8px rgba(110, 142, 251, 0.3);
}

.message-input button:active {
  transform: translateY(0);
}

.error-banner {
  background-color: #ffebee;
  color: #f44336;
  padding: 12px;
  text-align: center;
  border-top: 1px solid #f44336;
  font-size: 0.9rem;
  animation: fade 0.3s ease-in-out;
}

@keyframes fade {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Responsive styles */
@media (max-width: 768px) {
  .sidebar {
    width: 250px;
  }
  
  .message {
    max-width: 90%;
  }
  
  .user-info h3,
  .chat-header h3 {
    font-size: 1.2rem;
  }
}

@media (max-width: 576px) {
  .chat-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    max-height: 180px;
  }
  
  .users-list {
    padding: 10px;
  }
  
  .users-list ul {
    display: flex;
    overflow-x: auto;
  }
  
  .users-list li {
    display: inline-block;
    margin-right: 10px;
    white-space: nowrap;
  }
}

@media (min-width: 1200px) {
  .chat-container {
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .sidebar {
    width: 350px;
  }
  
  .message-input input {
    font-size: 1.2rem;
    padding: 18px 25px;
  }
  
  .message-input button {
    height: 60px;
    font-size: 1.2rem;
  }
}
</style> 