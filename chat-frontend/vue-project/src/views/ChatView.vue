<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ChatBox from '../components/ChatBox.vue';

const router = useRouter();
const username = ref('');

onMounted(() => {
  const storedUsername = localStorage.getItem('username');
  if (!storedUsername) {
    router.push('/login');
  } else {
    username.value = storedUsername;
  }
});
</script>

<template>
  <div class="chat-view">
    <ChatBox v-if="username" :username="username" />
  </div>
</template>

<style scoped>
.chat-view {
  height: 100vh;
  width: 100%;
}
</style> 