import { defineConfig } from "@pandacss/dev";

export default defineConfig({
  // bun panda codegen --watch
  // bun panda cssgen --watch -o src/styled-system/styles.css
  // 扫描文件路径
  include: ["./src/**/*.{js,jsx,ts,tsx,vue}"],
  exclude: [],

  // 关键：关闭全局样式重置，避免破坏同事的 CSS
  preflight: false,

  // 样式输出目录
  // 在 @pandacss/dev 1.8.x 里，styles.css 是 panda cssgen 生成的，不是 codegen。
  // bun panda cssgen -o src/styled-system/styles.css

  outdir: "src/styled-system",
  jsxFramework: 'vue',

  staticCss: {
    themes: ["light", "dark"]
  },

  // 主题配置 (复刻之前的深蓝/科技风)
  theme: {
    extend: {
      tokens: {
        colors: {
          brand: {
            primary: { value: "#1a74ff" },
            hover: { value: "#3b87ff" },
            bg: { value: "#0b1020" },
            surface: { value: "rgba(26, 116, 255, 0.12)" },
            text: {
              main: { value: "#0b1220" },
              dim: { value: "#5d6a85" }
            }
          },
          surface: {
            canvas: { value: "#f3f5fb" },
            base: { value: "#ffffff" },
            elevated: { value: "#f7f9ff" },
            sunken: { value: "#eef2f9" },
            outline: { value: "rgba(15, 23, 42, 0.12)" },
            outlineStrong: { value: "rgba(15, 23, 42, 0.18)" },
            text: { value: "#0b1220" },
            textDim: { value: "#5d6a85" },
            textHighlight: { value: "#f97316" }
          }
        },
        fonts: {
          mono: { value: "'IBM Plex Mono', monospace" },
          sans: { value: "'Space Grotesk', system-ui, sans-serif" }
        }
      }
    }
  },
  themes: {
    light: {
      tokens: {
      }
    },
    dark: {
      tokens: {
        colors: {
          brand: {
            primary: { value: "#4c8dff" },
            hover: { value: "#70a4ff" },
            bg: { value: "#0b1020" },
            surface: { value: "rgba(255, 255, 255, 0.06)" },
            text: {
              main: { value: "#e7edff" },
              dim: { value: "#9aa9c4" },
            }
          },
          surface: {
            canvas: { value: "#0b1020" },
            base: { value: "#111a2b" },
            elevated: { value: "#16213a" },
            sunken: { value: "#0e1627" },
            outline: { value: "rgba(203, 214, 255, 0.14)" },
            outlineStrong: { value: "rgba(203, 214, 255, 0.22)" },
            text: { value: "#e7edff" },
            textDim: { value: "#9aa9c4" }
          }
        }
      }
    }
  }
});
