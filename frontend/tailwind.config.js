export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#eef5ff",
          100: "#d9e9ff",
          700: "#16457a",
          800: "#123866",
          900: "#0b2340"
        }
      },
      boxShadow: {
        command: "0 14px 40px rgba(11, 35, 64, 0.10)"
      }
    }
  },
  plugins: []
};
