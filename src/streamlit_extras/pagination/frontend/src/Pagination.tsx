import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import {
  CSSProperties,
  FC,
  ReactElement,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

export type PaginationStateShape = {
  page: number;
};

export type PaginationDataShape = {
  num_pages: number;
  disabled: boolean;
  max_visible_pages: number | null;
  width: "content" | "stretch" | number;
};

export type PaginationProps = Pick<
  FrontendRendererArgs<PaginationStateShape, PaginationDataShape>,
  "setStateValue"
> & {
  numPages: number;
  disabled: boolean;
  maxVisiblePages: number | null;
  width: "content" | "stretch" | number;
};

type PageItem = { type: "page"; page: number } | { type: "ellipsis"; key: string };

// Constants for width calculations
const ITEM_WIDTH = 32;
const GAP = 4;
const ARROW_WIDTH = 32;

/**
 * Generates the page items to display based on the truncation algorithm.
 * Follows established patterns (Atlassian, Chakra UI, BaseWeb):
 * - Near start: `1 2 3 4 5 ... 20`
 * - In middle: `1 ... 5 6 7 ... 20`
 * - Near end: `1 ... 16 17 18 19 20`
 */
function getPageItems(
  numPages: number,
  currentPage: number,
  maxVisiblePages: number | null
): PageItem[] {
  // If no max or max is null, show all pages
  if (maxVisiblePages === null || numPages <= maxVisiblePages) {
    return Array.from({ length: numPages }, (_, i) => ({
      type: "page" as const,
      page: i + 1,
    }));
  }

  // Special cases for small maxVisiblePages
  if (maxVisiblePages === 0) {
    return [];
  }

  if (maxVisiblePages === 1) {
    return [{ type: "page", page: currentPage }];
  }

  if (maxVisiblePages === 2) {
    if (currentPage === 1) {
      return [
        { type: "page", page: 1 },
        { type: "page", page: numPages },
      ];
    } else if (currentPage === numPages) {
      return [
        { type: "page", page: 1 },
        { type: "page", page: numPages },
      ];
    } else {
      return [
        { type: "page", page: 1 },
        { type: "page", page: numPages },
      ];
    }
  }

  const items: PageItem[] = [];

  // Calculate how many slots we have for context pages
  // We always show first, last, and current page
  // So we have maxVisiblePages - 3 slots for context (if different from first/last/current)
  const contextSlots = Math.max(0, maxVisiblePages - 3);
  const siblingsPerSide = Math.floor(contextSlots / 2);

  // Determine which pages to show
  const showFirst = true;
  const showLast = numPages > 1;

  // Calculate the range around the current page
  let rangeStart = Math.max(2, currentPage - siblingsPerSide);
  let rangeEnd = Math.min(numPages - 1, currentPage + siblingsPerSide);

  // Adjust range if we're near the edges
  const totalRangeSlots = contextSlots + 1; // +1 for current page if it's in the middle

  if (currentPage <= siblingsPerSide + 2) {
    // Near the start - show more pages at the beginning
    rangeStart = 2;
    rangeEnd = Math.min(numPages - 1, 1 + totalRangeSlots);
  } else if (currentPage >= numPages - siblingsPerSide - 1) {
    // Near the end - show more pages at the end
    rangeEnd = numPages - 1;
    rangeStart = Math.max(2, numPages - totalRangeSlots);
  }

  // Build the items array
  if (showFirst) {
    items.push({ type: "page", page: 1 });
  }

  // Add left ellipsis if needed
  if (rangeStart > 2) {
    items.push({ type: "ellipsis", key: "left" });
  }

  // Add range pages
  for (let i = rangeStart; i <= rangeEnd; i++) {
    items.push({ type: "page", page: i });
  }

  // Add right ellipsis if needed
  if (rangeEnd < numPages - 1) {
    items.push({ type: "ellipsis", key: "right" });
  }

  // Add last page
  if (showLast && numPages > 1) {
    items.push({ type: "page", page: numPages });
  }

  return items;
}

/**
 * Calculate how many page items can fit in the available width.
 */
function calculateFittingPages(availableWidth: number): number {
  // Available width for page items = total - arrows - gaps around arrows
  const widthForItems = availableWidth - 2 * ARROW_WIDTH - 2 * GAP;

  if (widthForItems <= 0) return 0;

  // Each item takes ITEM_WIDTH + GAP (except the last one)
  // n items = n * ITEM_WIDTH + (n-1) * GAP
  // widthForItems >= n * ITEM_WIDTH + (n-1) * GAP
  // widthForItems >= n * (ITEM_WIDTH + GAP) - GAP
  // n <= (widthForItems + GAP) / (ITEM_WIDTH + GAP)
  const maxItems = Math.floor((widthForItems + GAP) / (ITEM_WIDTH + GAP));

  return Math.max(0, maxItems);
}

// CSS for focus-visible only (keyboard navigation)
const globalStyles = `
  .st-pagination-btn:focus {
    outline: none;
  }
  .st-pagination-btn:focus-visible {
    box-shadow: 0 0 0 2px var(--st-primary-color) !important;
  }
`;

/**
 * A pagination widget for Streamlit.
 *
 * Displays numbered page buttons with prev/next arrows and intelligent
 * truncation for large page counts.
 */
const Pagination: FC<PaginationProps> = ({
  numPages,
  disabled,
  maxVisiblePages,
  width,
  setStateValue,
}): ReactElement => {
  const [currentPage, setCurrentPage] = useState(1);
  const [containerWidth, setContainerWidth] = useState<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Set up ResizeObserver to track container width
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerWidth(entry.contentRect.width);
      }
    });

    resizeObserver.observe(container);

    // Initial measurement
    setContainerWidth(container.getBoundingClientRect().width);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  // Calculate effective maxVisiblePages based on available width
  const effectiveMaxVisiblePages = useMemo(() => {
    // If width is "content", don't apply responsive behavior
    if (width === "content") {
      return maxVisiblePages;
    }

    // If we don't have a measured width yet, use the provided maxVisiblePages
    if (containerWidth === null) {
      return maxVisiblePages;
    }

    const fittingPages = calculateFittingPages(containerWidth);

    // Use the smaller of maxVisiblePages (user preference) and fittingPages (responsive)
    if (maxVisiblePages === null) {
      return fittingPages;
    }

    return Math.min(maxVisiblePages, fittingPages);
  }, [containerWidth, maxVisiblePages, width]);

  const pageItems = useMemo(
    () => getPageItems(numPages, currentPage, effectiveMaxVisiblePages),
    [numPages, currentPage, effectiveMaxVisiblePages]
  );

  const handlePageChange = useCallback(
    (page: number) => {
      if (disabled || page < 1 || page > numPages) return;
      setCurrentPage(page);
      setStateValue("page", page);
    },
    [disabled, numPages, setStateValue]
  );

  const handlePrev = useCallback(() => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  }, [currentPage, handlePageChange]);

  const handleNext = useCallback(() => {
    if (currentPage < numPages) {
      handlePageChange(currentPage + 1);
    }
  }, [currentPage, numPages, handlePageChange]);

  // Container styles
  const containerStyle = useMemo<CSSProperties>(() => {
    const baseStyle: CSSProperties = {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: `${GAP}px`,
      fontFamily: "var(--st-font)",
      fontSize: "14px",
    };

    if (width === "stretch") {
      baseStyle.width = "100%";
    } else if (typeof width === "number") {
      baseStyle.width = `${width}px`;
    } else {
      // "content" - fit to content
      baseStyle.justifyContent = "flex-start";
    }

    return baseStyle;
  }, [width]);

  // Base button style
  const getButtonStyle = useCallback(
    (isActive: boolean, isDisabled: boolean): CSSProperties => {
      const baseStyle: CSSProperties = {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minWidth: `${ITEM_WIDTH}px`,
        height: `${ITEM_WIDTH}px`,
        padding: "0 8px",
        border: "1px solid",
        borderRadius: "6px",
        cursor: isDisabled ? "not-allowed" : "pointer",
        transition: "border-color 0.15s ease, background-color 0.15s ease",
        outline: "none",
        fontFamily: "inherit",
        fontSize: "inherit",
        fontWeight: isActive ? 600 : 400,
      };

      if (isDisabled) {
        return {
          ...baseStyle,
          backgroundColor: "transparent",
          borderColor: "var(--st-gray-60)",
          color: "var(--st-gray-60)",
          opacity: 0.5,
        };
      }

      if (isActive) {
        return {
          ...baseStyle,
          backgroundColor: "transparent",
          borderColor: "var(--st-text-color)",
          color: "var(--st-text-color)",
        };
      }

      return {
        ...baseStyle,
        backgroundColor: "transparent",
        borderColor: "transparent",
        color: "var(--st-text-color)",
      };
    },
    []
  );

  // Arrow button style
  const getArrowStyle = useCallback((isDisabled: boolean): CSSProperties => {
    return {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: `${ARROW_WIDTH}px`,
      height: `${ITEM_WIDTH}px`,
      padding: 0,
      border: "none",
      borderRadius: "6px",
      cursor: isDisabled ? "not-allowed" : "pointer",
      transition: "opacity 0.15s ease",
      outline: "none",
      backgroundColor: "transparent",
      color: isDisabled ? "var(--st-gray-60)" : "var(--st-text-color)",
      opacity: isDisabled ? 0.5 : 1,
      fontFamily: "inherit",
      fontSize: "16px",
      flexShrink: 0,
    };
  }, []);

  // Ellipsis style
  const ellipsisStyle = useMemo<CSSProperties>(
    () => ({
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minWidth: `${ITEM_WIDTH}px`,
      height: `${ITEM_WIDTH}px`,
      color: "var(--st-text-color)",
      userSelect: "none",
    }),
    []
  );

  const isPrevDisabled = disabled || currentPage === 1;
  const isNextDisabled = disabled || currentPage === numPages;

  return (
    <>
      <style>{globalStyles}</style>
      <div ref={containerRef} style={containerStyle}>
        {/* Previous button */}
        <button
          type="button"
          className="st-pagination-btn"
          style={getArrowStyle(isPrevDisabled)}
          onClick={handlePrev}
          disabled={isPrevDisabled}
          aria-label="Previous page"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M10 12L6 8L10 4"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        {/* Page items */}
        {pageItems.map((item) => {
          if (item.type === "ellipsis") {
            return (
              <span key={item.key} style={ellipsisStyle} aria-hidden="true">
                ...
              </span>
            );
          }

          const isActive = item.page === currentPage;
          const buttonKey = `page-${item.page}`;

          return (
            <button
              key={buttonKey}
              type="button"
              className="st-pagination-btn"
              style={getButtonStyle(isActive, disabled)}
              onClick={() => handlePageChange(item.page)}
              disabled={disabled}
              aria-label={`Page ${item.page}`}
              aria-current={isActive ? "page" : undefined}
            >
              {item.page}
            </button>
          );
        })}

        {/* Next button */}
        <button
          type="button"
          className="st-pagination-btn"
          style={getArrowStyle(isNextDisabled)}
          onClick={handleNext}
          disabled={isNextDisabled}
          aria-label="Next page"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M6 4L10 8L6 12"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </>
  );
};

export default Pagination;
