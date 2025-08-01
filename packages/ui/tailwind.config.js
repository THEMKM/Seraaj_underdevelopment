/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#FFD749",
        ink: "#101028",
        "pixel-coral": "#FF6B94",
        "pixel-mint": "#00D9FF",
        "pixel-lavender": "#9A48FF",
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'monospace'],
        body: ['Inter', 'sans-serif'],
      },
      spacing: {
        'px': '8px',
        'px-2': '16px',
        'px-3': '24px',
        'px-4': '32px',
      },
      animation: {
        'px-bounce': 'bounce 1s infinite steps(8)',
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.clip-px': {
          'clip-path': 'polygon(8px 0%, 100% 0%, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0% 100%, 0% 8px)',
        },
        '.shadow-px': {
          'box-shadow': '4px 4px 0px #101028',
        },
        '.border-px': {
          'border-width': '2px',
          'border-style': 'solid',
        },
      });
    },
  ],
};