const tocLinks = [...document.querySelectorAll("#toc a")];

// headings in document order, paired with their toc links
const headingEls = tocLinks
	.map((link) => document.getElementById(link.getAttribute("href").slice(1)))
	.filter(Boolean);

const visible = new Set();
let activeId = null;

function setActiveTocLink(id) {
	activeId = id;
	tocLinks.forEach((link) => {
		link.dataset.active =
			link.getAttribute("href") === `#${id}` ? "true" : "false";
	});
}

const observer = new IntersectionObserver(
	(entries) => {
		entries.forEach((entry) => {
			if (!entry.target.id) return;
			if (entry.isIntersecting) visible.add(entry.target.id);
			else visible.delete(entry.target.id);
		});

		const topVisible = headingEls.find((el) => visible.has(el.id));
		if (topVisible && topVisible.id !== activeId) {
			setActiveTocLink(topVisible.id);
		}
	},
	{ rootMargin: "0px 0px -60% 0px" },
);

headingEls.forEach((el) => {
	observer.observe(el);
});

tocLinks.forEach((link) => {
	link.addEventListener("click", () => {
		setActiveTocLink(link.getAttribute("href").slice(1));
	});
});
