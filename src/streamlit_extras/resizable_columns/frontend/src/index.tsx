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

/**
 * Collapse the component's element wrapper so it doesn't contribute to the
 * vertical block's flex gap. Walks up from the component mount point to find
 * the element container (direct child of stVerticalBlock) and hides it from
 * the layout flow.
 */
function collapseElementWrapper(startEl: Element): void {
  let el: HTMLElement | null = startEl as HTMLElement;
  for (let i = 0; i < 6 && el; i++) {
    const parent: HTMLElement | null = el.parentElement;
    if (!parent) break;
    const testId = parent.getAttribute("data-testid");
    if (
      testId === "stVerticalBlock" ||
      testId === "stMainBlockContainer" ||
      testId === "stMain"
    ) {
      // `el` is the direct child of the vertical block — collapse it
      el.style.marginBottom = "-1rem";
      el.style.height = "0";
      el.style.minHeight = "0";
      break;
    }
    el = parent;
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
  collapseElementWrapper(parentElement as unknown as Element);

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
