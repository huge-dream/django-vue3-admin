/** @type {import('tailwindcss').Config} */
module.exports = {
	content: ['./index.html', './src/**/*.{vue,js}'],
	theme: {
		extend: {
			height: {
				'screen/2': '50vh',
			},
		},
	},
	plugins: [],
};
