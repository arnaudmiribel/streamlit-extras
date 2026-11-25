// scroll to the active link in the sidebar on page load
const sidebar = document.querySelector('[data-sidebar="content"]');
const activeLink = sidebar?.querySelector('[data-active="true"]');

if (sidebar && activeLink) {
	const saved = sessionStorage.getItem("sidebar-scroll");

	if (saved !== null) {
		// restore the last offset
		sidebar.scrollTop = parseInt(saved, 10);
	}

	// calculate the offset of the active link relative to the sidebar
	offsetTop = activeLink.offsetTop;
	let parent = activeLink.parentElement;
	while (parent !== sidebar && parent !== null) {
		offsetTop += parent.offsetTop;
		parent = parent.parentElement;
	}

	sidebar.scrollTo({
		top: offsetTop - sidebar.clientHeight / 2,
		behavior: "smooth",
	});

	window.addEventListener("beforeunload", () => {
		sessionStorage.setItem("sidebar-scroll", sidebar.scrollTop);
	});
}
