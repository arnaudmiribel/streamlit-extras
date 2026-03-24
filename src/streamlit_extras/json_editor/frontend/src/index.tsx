import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import JsonEditor, {
  JsonEditorDataShape,
  JsonEditorStateShape,
} from "./JsonEditor";

// Handle the possibility of multiple instances of the component to keep track
// of the React roots for each component instance.
const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const JsonEditorRoot: FrontendRenderer<
  JsonEditorStateShape,
  JsonEditorDataShape
> = (args) => {
  const { data, parentElement, setStateValue } = args;

  // Get the react-root div from the parentElement that we defined in our
  // `st.components.v2.component` call in Python.
  const rootElement = parentElement.querySelector(".react-root");

  if (!rootElement) {
    throw new Error("Unexpected: React root element not found");
  }

  // Check to see if we already have a React root for this component instance.
  let reactRoot = reactRoots.get(parentElement);
  if (!reactRoot) {
    // If we don't, create a new root for the React application using the React
    // DOM API.
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  // Extract all configuration from data
  const {
    json_data,
    name,
    collapsed,
    theme,
    display_data_types,
    display_object_size,
    enable_clipboard,
    sort_keys,
    editable,
  } = data;

  // Render/re-render the React application into the root
  reactRoot.render(
    <StrictMode>
      <JsonEditor
        setStateValue={setStateValue}
        json_data={json_data}
        name={name}
        collapsed={collapsed}
        theme={theme}
        display_data_types={display_data_types}
        display_object_size={display_object_size}
        enable_clipboard={enable_clipboard}
        sort_keys={sort_keys}
        editable={editable}
      />
    </StrictMode>,
  );

  // Return a function to cleanup the React application
  return () => {
    const reactRoot = reactRoots.get(parentElement);

    if (reactRoot) {
      reactRoot.unmount();
      reactRoots.delete(parentElement);
    }
  };
};

export default JsonEditorRoot;
