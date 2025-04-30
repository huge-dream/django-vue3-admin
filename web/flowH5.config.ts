import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path, {resolve} from 'path';
import vueJsx from "@vitejs/plugin-vue-jsx";
import vueSetupExtend from "vite-plugin-vue-setup-extend";
import { terser } from 'rollup-plugin-terser';
import postcss from 'rollup-plugin-postcss';
import pxtorem from 'postcss-pxtorem';
const pathResolve = (dir: string) => {
  return resolve(__dirname, '.', dir);
};
export default defineConfig({
  build: {
    // outDir: '../backend/static/previewer',
    lib: {
      entry: path.resolve(__dirname, 'src/views/plugins/dvadmin3-flow-web/src/flowH5/index.ts'), // 库的入口文件
      name: 'previewer', // 库的全局变量名称
      fileName: (format) => `index.${format}.js`, // 输出文件名格式
    },
    rollupOptions: {
      input:{
        previewer: path.resolve(__dirname, 'src/views/plugins/dvadmin3-flow-web/src/flowH5/index.ts'),
      },
      external: ['vue','xe-utils'], // 指定外部依赖
      output:{
        // dir: '../backend/static/previewer', // 输出目录
        entryFileNames: 'index.[format].js', // 入口文件名格式
        format: 'commonjs',
        globals: {
          vue: 'Vue'
        },
        chunkFileNames: `[name].[hash].js`
      },
      plugins: [
        terser({
          compress: {
            drop_console: false, // 确保不移除 console.log
          },
        }),
        postcss({
          plugins: [
            pxtorem({
              rootValue: 37.5,
              unitPrecision: 5,
              propList: ['*'],
              selectorBlackList: [],
              replace: true,
              mediaQuery: false,
              minPixelValue: 0,
              exclude: /node_modules/i,
            }),
          ],
        }),
      ],
    },
  },
  plugins: [
    vue(),
    vueJsx(),
    vueSetupExtend(),
  ],
  resolve: {
    alias: {
      '/@': path.resolve(__dirname, 'src'), // '@' 别名指向 'src' 目录
      '@views': pathResolve('./src/views'),
      '/src':path.resolve(__dirname, 'src')
    },
  },
  css:{
    postcss:{

    }
  },
  define: {
    'process.env': {}
  }
});