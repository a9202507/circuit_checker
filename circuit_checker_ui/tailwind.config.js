/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pass: '#16a34a',
        fail: '#dc2626',
      }
    },
  },
  plugins: [],
}
