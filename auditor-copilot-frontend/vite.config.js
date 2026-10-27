import { defineConfig } from 'vite'
import tailwindcss from "@tailwindcss/vite"
import react from '@vitejs/plugin-react-swc'
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));


/**
 * Vite Configuration File
 *
 * This configuration sets up the Vite build tool for the React application.
 * It includes plugins for React (SWC) and Tailwind CSS, path aliases,
 * and development server settings.
 *
 * @see https://vitejs.dev/config/
 */
export default defineConfig({
  plugins: [
    // Uses SWC for fast Refresh
    react(),
    // Tailwind CSS integration
    tailwindcss()
  ],
  resolve: {
    // Configures path aliases for cleaner imports (e.g., import ... from "@/components/...")
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
  server: {
    // Expose the server to the network
    host: true,
    // Run the development server on port 3000
    port: 3000,
  },
})
