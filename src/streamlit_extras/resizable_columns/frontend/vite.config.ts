import react from "@vitejs/plugin-react";
import process from "node:process";
import { defineConfig, UserConfig } from "vite";

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
      lib: {
        entry: "./src/index.tsx",
        name: "ResizableColumns",
        formats: ["es"],
        fileName: "index-[hash]",
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
