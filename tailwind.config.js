module.exports = {
  content: ['./dist/**/*.html', './dist/**/*.js'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'] },
      colors: {
        cream: '#f5efe3', paper: '#fffdf7', ink: '#2c2418', brown: '#5a4a34', line: '#e2dcd0',
        rust: '#c13b1b', brand: '#2c6e9e', 'brand-dark': '#1e4a6e', muted: '#6b5b45',
      },
    },
  },
  plugins: [],
};
