# Build with an agent

An AI coding agent can help draft an extra, compare component approaches, write a gallery example, and run checks. It cannot establish that the result is useful, accessible, safe, or compatible without a human review and actual tests.

## Give the agent a concrete goal

Describe the interaction, the inputs and outputs, and where the result should appear in a Streamlit app. Ask it to follow existing extras rather than adding a new framework. Provide visual references or expected keyboard behavior for UI work.

For example:

> Add a small extra that presents three choices in a Streamlit app. Follow the nearest existing extra, provide a runnable gallery example, use the app theme, and test selection and keyboard interaction.

## What to check before a pull request

- Confirm the public Python API is typed, the example runs, and the UI looks coherent in Streamlit's light and dark themes.
- Check that HTML derived from user input is escaped and any frontend component handles state and cleanup correctly.
- Run `uv run pytest` and `uv run ruff check .`; run `npm run build` for an edited React frontend and `uv build` for packaging changes.
- Review the output in the [gallery](https://github.com/arnaudmiribel/streamlit-extras/blob/main/gallery/streamlit_app.py) and attach a screenshot for visual changes.

Start with the [contribution guide](contributing.md), the repository [AGENTS.md](https://github.com/arnaudmiribel/streamlit-extras/blob/main/AGENTS.md), and the [component guidance](https://github.com/arnaudmiribel/streamlit-extras/blob/main/src/streamlit_extras/AGENTS.md). For tools that read website indexes, a plain-text [llms.txt](llms.txt) is available at the docs root.
