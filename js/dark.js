const darkTheme = window.matchMedia("(prefers-color-scheme: dark)");
darkTheme.onchange = (e) => {
	if (e.matches) {
		document.documentElement.classList.add("dark");
		localStorage.theme = "dark";
	} else {
		document.documentElement.classList.remove("dark");
		localStorage.removeItem("theme");
	}
};

// On page load. Priotiry to lcaolStorage
if (localStorage.theme === "dark") {
	document.documentElement.classList.add("dark");
} else if (localStorage.theme === "light") {
	document.documentElement.classList.remove("dark");
} else if (darkTheme.matches) {
	document.documentElement.classList.add("dark");
} else {
	document.documentElement.classList.remove("dark");
}

// set the layout based on localStorage
document.documentElement.classList.add(
	localStorage.getItem("html-layout") || "layout-fixed",
);
