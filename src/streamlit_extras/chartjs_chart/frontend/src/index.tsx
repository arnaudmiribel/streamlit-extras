import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import ChartJSChart, { ChartJSChartDataShape } from "./ChartJSChart";

// Handle the possibility of multiple instances of the component to keep track
// of the React roots for each component instance.
const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

// This component is display-only, so we use an empty state shape
type ChartJSStateShape = Record<string, never>;

const ChartJSChartRoot: FrontendRenderer<
  ChartJSStateShape,
  ChartJSChartDataShape
> = (args) => {
  const { data, parentElement } = args;

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
    // @see https://react.dev/reference/react-dom/client/createRoot
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  // Extract data passed from Streamlit on the Python side.
  const { spec, height, theme } = data;

  // Render/re-render the React application into the root using the React DOM
  // API.
  reactRoot.render(
    <StrictMode>
      <ChartJSChart spec={spec} height={height} theme={theme} />
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

export default ChartJSChartRoot;
