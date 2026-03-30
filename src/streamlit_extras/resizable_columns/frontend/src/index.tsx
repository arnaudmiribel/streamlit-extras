import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import ResizableColumns, {
  ResizableColumnsDataShape,
  ResizableColumnsStateShape,
} from "./ResizableColumns";

const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

function forceOverflowVisible(startEl: Element): void {
  let el: Element | null = startEl;
  for (let i = 0; i < 6 && el; i++) {
    const htmlEl = el as HTMLElement;
    if (htmlEl.style) {
      htmlEl.style.overflow = "visible";
      htmlEl.style.position = "relative";
      htmlEl.style.zIndex = "1000";
    }
    el = el.parentElement;
  }
}

const ResizableColumnsRoot: FrontendRenderer<
  ResizableColumnsStateShape,
  ResizableColumnsDataShape
> = (args) => {
  const { data, parentElement, setStateValue } = args;

  const rootElement = parentElement.querySelector(".react-root");

  if (!rootElement) {
    throw new Error("Unexpected: React root element not found");
  }

  forceOverflowVisible(parentElement as unknown as Element);

  let reactRoot = reactRoots.get(parentElement);
  if (!reactRoot) {
    reactRoot = createRoot(rootElement);
    reactRoots.set(parentElement, reactRoot);
  }

  const { num_columns, widths, min_width } = data;

  reactRoot.render(
    <StrictMode>
      <ResizableColumns
        setStateValue={setStateValue}
        numColumns={num_columns}
        widths={widths}
        minWidth={min_width}
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

export default ResizableColumnsRoot;
