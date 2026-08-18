import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { densityChineseExtraPlugin } from './density-localize-extra-plugin.js'
import { densityChinesePlugin } from './density-localize-plugin.js'
import { densityTaskBehaviorPlugin } from './density-task-behavior-plugin.js'

export default defineConfig({
  plugins: [densityTaskBehaviorPlugin(), densityChineseExtraPlugin(), densityChinesePlugin(), vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true
      }
    }
  }
})
