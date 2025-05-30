import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    {
      name: 'client-ip-handler',
      configureServer(server) {
        server.middlewares.use('/api/get-client-ip', (req, res) => {
          const clientIP = req.socket.remoteAddress || 
                          req.headers['x-forwarded-for'] || 
                          '127.0.0.1';
          
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ ip: clientIP }));
        });
      }
    }
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      // Proxy API requests to backend
      '/api': {
        target: 'http://192.168.1.5:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
