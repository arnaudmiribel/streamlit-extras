import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import DirectoryTree, {
  DirectoryTreeDataShape,
  DirectoryTreeStateShape,
} from "./DirectoryTree";

const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const DirectoryTreeRoot: FrontendRenderer<
  DirectoryTreeStateShape,
  DirectoryTreeDataShape
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

  const { tree, expand_depth, border, color, selectable, height } = data;

  reactRoot.render(
    <StrictMode>
      <DirectoryTree
        tree={tree}
        expandDepth={expand_depth}
        border={border}
        color={color}
        selectable={selectable}
        height={height}
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

export default DirectoryTreeRoot;
