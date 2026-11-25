const CURRENT_VERSION = new URL(base_url).pathname.split("/")[1];

const VERSIONS_URL = new URL(`${base_url}/../versions.json`, window.location);

function selectVersion(version) {
	// get root without version prefixed like https://domain:port/base_dir/
	const root = new URL(`${base_url}/../`, window.location);
	const url = new URL(window.location.href); // https://domain:port/base_dir/[version]/a/b/c
	const rest = url.pathname.slice(root.pathname.length); // [version]/a/b/c
	url.pathname = root.pathname + rest.replace(/^[^/]+/, version);
	window.location.href = url.href;
}

// run the fetch directly
fetch(VERSIONS_URL.href)
	.then((res) => {
		if (!res.ok) {
			throw new Error("Could not locate versions.json");
		}
		console.log("Docs versions loaded from:", VERSIONS_URL.href);
		return res.json();
	})
	.then((data) => {
		const select = document.getElementById("version-selector");
		if (!select) {
			return;
		}
		for (const item of data) {
			const alias = item.aliases.length ? ` (${item.aliases.join(", ")})` : "";
			const opt = document.createElement("option");
			opt.innerText = item.title + alias;
			opt.setAttribute("value", item.version);
			if (item.version === CURRENT_VERSION) {
				opt.setAttribute("selected", true);
			}
			select.appendChild(opt);
		}
	})
	.catch((e) => {
		console.error(e);
	});
