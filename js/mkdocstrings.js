for (const el of document.querySelectorAll(
	".typography .doc code.language-python",
)) {
	el.classList.add("codehilite");
}

for (const el of document.querySelectorAll("article .doc .doc-contents")) {
	el.innerHTML = el.innerHTML.trim();
}
