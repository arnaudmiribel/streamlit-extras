import react from "@vitejs/plugin-react";
import process from "node:process";
import { defineConfig, UserConfig } from "vite";

/**
 * Vite configuration for Streamlit Custom Component v2 development using React.
 */
export default defineConfig(() => {
  const isProd = process.env.NODE_ENV === "production";
  const isDev = !isProd;

  return {
    base: "./",
    plugins: [react()],
    define: {
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    },
    build: {
      minify: isDev ? false : "esbuild",
      outDir: "build",
      sourcemap: isDev,
      // Output CSS as a separate file so it can be injected into shadow DOM
      cssCodeSplit: false,
      lib: {
        entry: "./src/index.tsx",
        name: "DataframeFilter",
        formats: ["es"],
        fileName: "index-[hash]",
      },
      rollupOptions: {
        output: {
          // Ensure CSS is output as a separate file with hash
          assetFileNames: "index-[hash][extname]",
        },
      },
      ...(!isDev && {
        esbuild: {
          drop: ["console", "debugger"],
          minifyIdentifiers: true,
          minifySyntax: true,
          minifyWhitespace: true,
        },
      }),
    },
  } satisfies UserConfig;
});
