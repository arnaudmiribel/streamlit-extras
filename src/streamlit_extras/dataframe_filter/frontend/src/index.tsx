import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import DataframeFilter, {
  DataframeFilterDataShape,
  DataframeFilterStateShape,
} from "./DataframeFilter";

// Import CSS - Vite will extract this into a separate file
import "./styles.css";

// Handle the possibility of multiple instances of the component
const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const DataframeFilterRoot: FrontendRenderer<
  DataframeFilterStateShape,
  DataframeFilterDataShape
> = (args) => {
  const { data, parentElement, setStateValue } = args;

  const rootElement = parentElement.querySelector(".react-root");

  if (!rootElement) {
    throw new Error("Unexpected: React root element not found");
  }

  let reactRoot = reactRoots.get(parentElement);
  if (!reactRoot) {
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  const { columns } = data;

  reactRoot.render(
    <StrictMode>
      <DataframeFilter
        columns={columns}
        setStateValue={setStateValue}
      />
    </StrictMode>,
  );

  return () => {
    const reactRoot = reactRoots.get(parentElement);
    if (reactRoot) {
      reactRoot.unmount();
      reactRoots.delete(parentElement);
    }
  };
};

export default DataframeFilterRoot;
