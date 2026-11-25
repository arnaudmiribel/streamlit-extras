// attach input event listener to all sliders, to update the progress bar
for (const i of document.querySelectorAll('article input[type="range"]')) {
	const prev = i.oninput;
	i.oninput = (event) => {
		const slider = event.target;
		const value = slider.value;
		const min = slider.min ? slider.min : 0;
		const max = slider.max ? slider.max : 100;
		const percentage = ((value - min) / (max - min)) * 100;
		slider.style.setProperty("--progress", `${percentage}%`);
		if (prev) {
			prev(event);
		}
	};
}
