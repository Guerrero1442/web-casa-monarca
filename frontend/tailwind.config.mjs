/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{astro,html,js,jsx,md,mdx,pure,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#F5F3ED",
        primary: {
          DEFAULT: "#C36B53",
          hover: "#A85A45", // Variante para estados interactivos
        },
        secondary: {
          DEFAULT: "#23352F",
          hover: "#1A2823",
        },
        surface: "#FFFFFF",
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'pill': '9999px',
      }
    },
  },
  plugins: [],
}
