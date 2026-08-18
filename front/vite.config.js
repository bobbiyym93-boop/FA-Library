import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { densityChinesePlugin } from './density-localize-plugin.js'

export default defineConfig({
  plugins: [densityChinesePlugin(), vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
})
