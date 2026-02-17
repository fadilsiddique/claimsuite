import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { VitePWA } from 'vite-plugin-pwa'
import Icons from 'unplugin-icons/vite'

export default defineConfig(({ command }) => {
  const isDev = command === 'serve'

  // Read webserver port for dev proxy
  let proxyConfig = {}
  if (isDev) {
    try {
      const { webserver_port } = require('../../../sites/common_site_config.json')
      proxyConfig = {
        '^/(api|login|assets|files)': {
          target: `http://127.0.0.1:${webserver_port}`,
          ws: true,
          router: (req) => {
            const site = req.headers.host?.split(':')[0]
            return `http://${site}:${webserver_port}`
          },
        },
      }
    } catch (e) {
      // common_site_config not available
    }
  }

  return {
    plugins: [
      vue(),
      Icons({ compiler: 'vue3' }),
      VitePWA({
        registerType: 'autoUpdate',
        workbox: {
          globPatterns: ['**/*.{js,css,html,png,svg,woff,woff2}'],
          navigateFallback: null,
          runtimeCaching: [
            {
              urlPattern: /^\/api\//,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: { maxEntries: 50, maxAgeSeconds: 300 },
              },
            },
          ],
        },
        manifest: {
          name: 'ClaimSuite',
          short_name: 'ClaimSuite',
          description: 'Expense claim management',
          theme_color: '#ffffff',
          background_color: '#f9fafb',
          display: 'standalone',
          start_url: '/frontend',
          scope: '/frontend',
          icons: [
            {
              src: '/assets/claimsuite/frontend/icons/icon-192x192.png',
              sizes: '192x192',
              type: 'image/png',
            },
            {
              src: '/assets/claimsuite/frontend/icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
            },
            {
              src: '/assets/claimsuite/frontend/icons/icon-512x512.png',
              sizes: '512x512',
              type: 'image/png',
              purpose: 'maskable',
            },
          ],
        },
      }),
    ],
    server: {
      port: 8080,
      host: true,
      proxy: proxyConfig,
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    build: {
      outDir: `../${path.basename(path.resolve('..'))}/public/frontend`,
      emptyOutDir: true,
      target: 'es2015',
    },
    base: isDev ? '/frontend/' : '/assets/claimsuite/frontend/',
    optimizeDeps: {
      include: [
        'frappe-ui > feather-icons',
        'showdown',
        'engine.io-client',
        'engine.io-client > debug',
      ],
    },
  }
})
