import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
    css: true,
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
    coverage: {
      reporter: ["text", "html"],
      include: ["src/services/**/*.ts", "src/components/**/*.tsx", "src/hooks/**/*.ts"],
    },
  },
});
