function randomString(length = 10) {
	const chars =
		"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
	const array = new Uint32Array(length);
	crypto.getRandomValues(array);
	return Array.from(array, (x) => chars[x % chars.length]).join("");
}

/**
 * Executes code using Programiz REPL via socket.io
 * @param {string} lang - Programming language (e.g., "python", "cpp", "javascript")
 * @param {string} code - Code to execute
 * @returns {Promise<{output:string,ok:boolean}>} Promise resolving to the output
 */
function runCodexec(code, lang) {
	console.log(`Running code in ${lang}:`, code);
	if (
		![
			"r",
			"c",
			"cpp",
			"csharp",
			"java",
			"python",
			"javascript",
			"typescript",
			"scala",
			"dart",
			"ruby",
			"golang",
			"php",
			"swift",
			"rust",
		].includes(lang)
	) {
		return Promise.reject(new Error(`Unsupported language: ${lang}`));
	}
	const sessionId = randomString();
	const socket = io(`wss://${lang}.repl-web.programiz.com`, {
		path: "/socket.io",
		transports: ["websocket"],
		query: {
			sessionId,
			lang,
			EIO: "3",
		},
	});

	const id = `${lang}/${sessionId}`;

	return new Promise((resolve, reject) => {
		let timeout;
		let result = "";
		let ok = true;

		socket.on("connect_error", (err) => {
			console.error(`[${id}] Connection error:`, err);
			reject(err);
		});

		socket.on("connect", () => {
			console.log(`[${id}] Connected`);
			console.log(`[${id}] Code:\n${code}`);
			socket.emit("run", { code });
		});

		socket.on("disconnect", () => {
			clearTimeout(timeout);
			// remove bottom marker and trim
			result = result.replace("=== Code Execution Successful ===", "").trim(); // trim trailing newlines
			resolve({ output: result, ok });
			console.log(`[${id}] Disconnected`);
		});

		socket.on("output", ({ output }) => {
			console.log(`[${id}] Output received:`, output);
			if (output.slice(0, 6) === "ERROR!") {
				ok = false;
				// we try to retrieve the error message in the next message
				return;
			}
			// append output
			result += output;
		});

		// safety timeout
		timeout = setTimeout(() => {
			reject(new Error(`[${id}] Timeout while waiting for output`));
			socket.disconnect();
		}, 10000);
	});
}
