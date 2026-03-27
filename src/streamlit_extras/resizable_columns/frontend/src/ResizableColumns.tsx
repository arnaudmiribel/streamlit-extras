import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import {
  CSSProperties,
  FC,
  ReactElement,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

export type ResizableColumnsStateShape = {
  widths: number[];
};

export type ResizableColumnsDataShape = {
  num_columns: number;
  widths: number[];
  min_width: number;
};

export type ResizableColumnsProps = Pick<
  FrontendRendererArgs<ResizableColumnsStateShape, ResizableColumnsDataShape>,
  "setStateValue"
> & {
  numColumns: number;
  widths: number[];
  minWidth: number;
};

function findColumnsContainer(componentEl: HTMLElement): HTMLElement | null {
  let wrapper: HTMLElement | null = componentEl;
  while (wrapper) {
    const parent: HTMLElement | null = wrapper.parentElement;
    if (!parent) break;
    const testId = parent.getAttribute("data-testid");
    if (testId === "stVerticalBlock" || testId === "stMainBlockContainer" || testId === "stMain") {
      break;
    }
    wrapper = parent;
  }

  let sibling = wrapper?.nextElementSibling as HTMLElement | null;
  while (sibling) {
    if (sibling.getAttribute("data-testid") === "stHorizontalBlock") return sibling;
    const horizontal = sibling.querySelector(
      '[data-testid="stHorizontalBlock"]',
    );
    if (horizontal) return horizontal as HTMLElement;
    sibling = sibling.nextElementSibling as HTMLElement | null;
  }
  return null;
}

function forceOverflowVisible(el: HTMLElement): void {
  let current: HTMLElement | null = el;
  for (let i = 0; i < 8 && current; i++) {
    current.style.overflow = "visible";
    current = current.parentElement;
  }
}

function ensureHandlesAboveColumns(columnsEl: HTMLElement): void {
  const children = columnsEl.children;
  for (let i = 0; i < children.length; i++) {
    const col = children[i] as HTMLElement;
    const style = window.getComputedStyle(col);
    if (style.position !== "static" || style.zIndex !== "auto") {
      col.style.zIndex = "1";
    }
  }
}

const ResizableColumns: FC<ResizableColumnsProps> = ({
  numColumns,
  widths,
  minWidth,
  setStateValue,
}): ReactElement => {
  const containerRef = useRef<HTMLDivElement>(null);
  const widthsRef = useRef<number[]>(widths);
  const [handleHeight, setHandleHeight] = useState(300);
  const columnsElRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    widthsRef.current = widths;
  }, [widths]);

  const refreshColumnsRef = useCallback(() => {
    const container = containerRef.current;
    if (!container) return null;
    forceOverflowVisible(container);
    const el = findColumnsContainer(container);
    columnsElRef.current = el;
    if (el) ensureHandlesAboveColumns(el);
    return el;
  }, []);

  useEffect(() => {
    const el = refreshColumnsRef();
    if (!el) return;

    const measure = () => {
      const current = columnsElRef.current;
      if (!current || !current.isConnected) {
        const fresh = refreshColumnsRef();
        if (!fresh) return;
      }
      const target = columnsElRef.current;
      if (!target) return;
      const rect = target.getBoundingClientRect();
      if (rect.height > 0) setHandleHeight(rect.height);
    };

    measure();

    const resizeObserver = new ResizeObserver(measure);
    resizeObserver.observe(el);

    const mutationObserver = new MutationObserver(() => {
      refreshColumnsRef();
      measure();
    });
    const parent = el.parentElement;
    if (parent) {
      mutationObserver.observe(parent, { childList: true, subtree: true });
    }

    return () => {
      resizeObserver.disconnect();
      mutationObserver.disconnect();
    };
  }, [numColumns, refreshColumnsRef]);

  const applyWidthsToDOM = useCallback((newWidths: number[]) => {
    let columnsEl = columnsElRef.current;
    if (!columnsEl || !columnsEl.isConnected) {
      columnsEl = refreshColumnsRef();
    }
    if (!columnsEl) return;
    const children = columnsEl.children;
    for (let i = 0; i < children.length && i < newWidths.length; i++) {
      const col = children[i] as HTMLElement;
      col.style.flex = `${newWidths[i]} 1 0%`;
      col.style.minWidth = "0px";
    }
  }, [refreshColumnsRef]);

  const handleMouseDown = useCallback(
    (dividerIndex: number) => (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      const container = containerRef.current;
      if (!container) return;

      refreshColumnsRef();

      const containerRect = container.getBoundingClientRect();
      const containerWidth = containerRect.width;
      const startX = e.clientX;
      const startWidths = [...widthsRef.current];
      const minFraction = minWidth / containerWidth;

      const handleMouseMove = (moveEvent: MouseEvent) => {
        const deltaX = moveEvent.clientX - startX;
        const deltaFraction = deltaX / containerWidth;

        const newWidths = [...startWidths];
        const leftIdx = dividerIndex;
        const rightIdx = dividerIndex + 1;

        let newLeft = startWidths[leftIdx] + deltaFraction;
        let newRight = startWidths[rightIdx] - deltaFraction;

        if (newLeft < minFraction) {
          newRight = newRight - (minFraction - newLeft);
          newLeft = minFraction;
        }
        if (newRight < minFraction) {
          newLeft = newLeft - (minFraction - newRight);
          newRight = minFraction;
        }

        newLeft = Math.max(newLeft, minFraction);
        newRight = Math.max(newRight, minFraction);

        newWidths[leftIdx] = newLeft;
        newWidths[rightIdx] = newRight;

        widthsRef.current = newWidths;

        const handles = container.querySelectorAll("[data-handle]");
        let cumulative = 0;
        for (let i = 0; i < handles.length; i++) {
          cumulative += newWidths[i];
          (handles[i] as HTMLElement).style.left = `${cumulative * 100}%`;
        }

        applyWidthsToDOM(newWidths);
      };

      const handleMouseUp = () => {
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        setStateValue("widths", widthsRef.current);
      };

      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    },
    [minWidth, setStateValue, applyWidthsToDOM, refreshColumnsRef],
  );

  useEffect(() => {
    const raf = requestAnimationFrame(() => {
      applyWidthsToDOM(widthsRef.current);
    });
    return () => cancelAnimationFrame(raf);
  });

  const containerStyle: CSSProperties = {
    position: "relative",
    width: "100%",
    height: "0px",
    overflow: "visible",
  };

  const handles: ReactElement[] = [];
  let cumulative = 0;
  for (let i = 0; i < numColumns - 1; i++) {
    cumulative += widths[i];
    handles.push(
      <Handle
        key={`handle-${i}`}
        left={cumulative * 100}
        height={handleHeight}
        onMouseDown={handleMouseDown(i)}
      />,
    );
  }

  return (
    <div ref={containerRef} style={containerStyle}>
      {handles}
    </div>
  );
};

const Handle: FC<{
  left: number;
  height: number;
  onMouseDown: (e: React.MouseEvent) => void;
}> = ({ left, height, onMouseDown }) => {
  return (
    <div
      data-handle=""
      onMouseDown={onMouseDown}
      style={{
        position: "absolute",
        left: `${left}%`,
        top: "0px",
        transform: "translateX(-50%)",
        width: "16px",
        height: `${height}px`,
        cursor: "col-resize",
        zIndex: 999,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: `${height * 0.1}px 0`,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          width: "0px",
          height: "100%",
          pointerEvents: "none",
        }}
      />
    </div>
  );
};

export default ResizableColumns;
