import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import SigmaGraph, { SigmaGraphDataShape, SigmaGraphStateShape } from "./SigmaGraph";

// Handle the possibility of multiple instances of the component to keep track
// of the React roots for each component instance.
const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const SigmaGraphRoot: FrontendRenderer<
  SigmaGraphStateShape,
  SigmaGraphDataShape
> = (args) => {
  const { data, parentElement, setStateValue } = args;

  // Get the sigma-root div from the parentElement that we defined in our
  // `st.components.v2.component` call in Python.
  const rootElement = parentElement.querySelector(".sigma-root");

  if (!rootElement) {
    throw new Error("Unexpected: Sigma root element not found");
  }

  // Check to see if we already have a React root for this component instance.
  let reactRoot = reactRoots.get(parentElement);
  if (!reactRoot) {
    // If we don't, create a new root for the React application using the React
    // DOM API.
    // @see https://react.dev/reference/react-dom/client/createRoot
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  // Extract data passed from Streamlit on the Python side.
  const {
    graph,
    useForceLayout,
    width,
    height,
    nodeColor,
    edgeColor,
    nodeSizeConfig,
    selectionMode,
    selectionEnabled,
    currentSelection,
  } = data;

  // Render/re-render the React application into the root using the React DOM
  // API.
  reactRoot.render(
    <StrictMode>
      <SigmaGraph
        setStateValue={setStateValue}
        graph={graph}
        useForceLayout={useForceLayout}
        width={width}
        height={height}
        nodeColor={nodeColor}
        edgeColor={edgeColor}
        nodeSizeConfig={nodeSizeConfig}
        selectionMode={selectionMode}
        selectionEnabled={selectionEnabled}
        currentSelection={currentSelection}
      />
    </StrictMode>,
  );

  // Return a function to cleanup the React application in the Streamlit
  // component lifecycle.
  return () => {
    const reactRoot = reactRoots.get(parentElement);

    if (reactRoot) {
      reactRoot.unmount();
      reactRoots.delete(parentElement);
    }
  };
};

export default SigmaGraphRoot;
