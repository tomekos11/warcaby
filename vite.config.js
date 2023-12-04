import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'My_app/frontend/static', // Specify your desired output directory
    publicDir: 'My_app/frontend/static',
    assetsDir: '',
    rollupOptions: {
      input: 'My_app/frontend/js/app.js', // specify your entry file here
    },
    manifest: true,
  },
})
