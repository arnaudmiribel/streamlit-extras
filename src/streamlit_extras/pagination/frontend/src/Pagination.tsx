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

type PageItem =
  | { type: "page"; page: number }
  | { type: "ellipsis"; key: string };

// Constants for width calculations
const ITEM_WIDTH = 32;
const GAP = 4;
const ARROW_WIDTH = 32;

/**
 * Display mode for responsive pagination.
 * Progressive degradation as container width decreases:
 * - "full": Show page numbers with truncation
 * - "current-only": Show only arrows and current page (< | 5 | >)
 * - "arrows-only": Show only arrows (< | >)
 */
type DisplayMode = "full" | "current-only" | "arrows-only";

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
  maxVisiblePages: number | null,
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
    // Show current page and last page (with ellipsis if not adjacent)
    // If current is the last page, show first and last instead
    if (currentPage === numPages) {
      // Current is last page: show first and last
      const items: PageItem[] = [{ type: "page", page: 1 }];
      // Add ellipsis if first and last are not adjacent
      if (numPages > 2) {
        items.push({ type: "ellipsis", key: "middle" });
      }
      items.push({ type: "page", page: numPages });
      return items;
    } else {
      // Show current and last
      const items: PageItem[] = [{ type: "page", page: currentPage }];
      // Add ellipsis if current and last are not adjacent
      if (currentPage < numPages - 1) {
        items.push({ type: "ellipsis", key: "middle" });
      }
      items.push({ type: "page", page: numPages });
      return items;
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
 * Calculate how many page buttons (not including ellipsis) can fit in the available width.
 * This is conservative - it reserves space for up to 2 ellipsis that might be added.
 */
function calculateFittingPages(availableWidth: number): number {
  // Available width for page items = total - arrows - gaps around arrows
  const widthForItems = availableWidth - 2 * ARROW_WIDTH - 2 * GAP;

  if (widthForItems <= 0) return 0;

  // Reserve space for up to 2 ellipsis (they take the same space as page buttons)
  // This ensures we don't overflow when ellipsis are added
  const ellipsisReserve = 2 * (ITEM_WIDTH + GAP);
  const availableForPages = widthForItems - ellipsisReserve;

  if (availableForPages <= 0) return 1; // At minimum, show 1 page

  // Each item takes ITEM_WIDTH + GAP (except the last one)
  // n items = n * ITEM_WIDTH + (n-1) * GAP
  // availableForPages >= n * ITEM_WIDTH + (n-1) * GAP
  // availableForPages >= n * (ITEM_WIDTH + GAP) - GAP
  // n <= (availableForPages + GAP) / (ITEM_WIDTH + GAP)
  const maxItems = Math.floor((availableForPages + GAP) / (ITEM_WIDTH + GAP));

  return Math.max(1, maxItems);
}

/**
 * Determine the display mode based on available width.
 * Implements progressive degradation:
 * 1. Full: enough space for at least 3 page items
 * 2. Current-only: only space for current page (< | n | >)
 * 3. Arrows-only: no space for any page items (< | >)
 */
function calculateDisplayMode(availableWidth: number): DisplayMode {
  // Minimum width for arrows only: 2 arrows + gap between them
  const arrowsOnlyWidth = 2 * ARROW_WIDTH + GAP;

  // Minimum width for current page only: arrows + 1 page item + gaps
  const currentOnlyWidth = 2 * ARROW_WIDTH + ITEM_WIDTH + 2 * GAP;

  // Minimum width for full mode: arrows + at least 3 page items (first, current, last) + gaps
  const fullModeMinWidth = 2 * ARROW_WIDTH + 3 * ITEM_WIDTH + 4 * GAP;

  if (availableWidth >= fullModeMinWidth) {
    return "full";
  } else if (availableWidth >= currentOnlyWidth) {
    return "current-only";
  } else if (availableWidth >= arrowsOnlyWidth) {
    return "arrows-only";
  }

  // Even if very narrow, still show arrows-only
  return "arrows-only";
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

  // Set up ResizeObserver to track container width for responsive behavior
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

  // Calculate display mode based on available width
  // Progressive degradation: full -> current-only -> arrows-only
  const displayMode = useMemo<DisplayMode>(() => {
    // If no measured width yet, assume full mode
    if (containerWidth === null) {
      return "full";
    }

    return calculateDisplayMode(containerWidth);
  }, [containerWidth]);

  // Calculate effective maxVisiblePages based on available width
  const effectiveMaxVisiblePages = useMemo(() => {
    // In non-full display modes, this value isn't used
    if (displayMode !== "full") {
      return 0;
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
  }, [containerWidth, maxVisiblePages, displayMode]);

  // Generate page items based on display mode
  const pageItems = useMemo(() => {
    // In arrows-only mode, show no page items
    if (displayMode === "arrows-only") {
      return [];
    }

    // In current-only mode, show only the current page
    if (displayMode === "current-only") {
      return [{ type: "page" as const, page: currentPage }];
    }

    // Full mode: use normal truncation algorithm
    return getPageItems(numPages, currentPage, effectiveMaxVisiblePages);
  }, [numPages, currentPage, effectiveMaxVisiblePages, displayMode]);

  const handlePageChange = useCallback(
    (page: number) => {
      if (disabled || page < 1 || page > numPages) return;
      setCurrentPage(page);
      setStateValue("page", page);
    },
    [disabled, numPages, setStateValue],
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

  // Outer container styles - handles width and centering
  const outerContainerStyle = useMemo<CSSProperties>(() => {
    const baseStyle: CSSProperties = {
      display: "flex",
      justifyContent: "center", // Center the inner content
      maxWidth: "100%",
    };

    if (width === "stretch") {
      baseStyle.width = "100%";
    } else if (typeof width === "number") {
      baseStyle.width = `${width}px`;
    } else {
      // "content" - fit to content but respect parent bounds
      baseStyle.justifyContent = "flex-start";
      baseStyle.width = "100%";
    }

    return baseStyle;
  }, [width]);

  // Inner container styles - groups all pagination elements together
  const innerContainerStyle = useMemo<CSSProperties>(() => {
    // Minimum width to always show arrows: 2 arrows + gap
    const minArrowsWidth = 2 * ARROW_WIDTH + GAP;

    return {
      display: "flex",
      alignItems: "center",
      gap: `${GAP}px`,
      fontFamily: "var(--st-font)",
      fontSize: "14px",
      minWidth: `${minArrowsWidth}px`, // Always show arrows
      maxWidth: "100%",
    };
  }, []);

  // Style for the page items wrapper (allows overflow hiding without affecting arrows)
  const pageItemsWrapperStyle = useMemo<CSSProperties>(
    () => ({
      display: "flex",
      alignItems: "center",
      gap: `${GAP}px`,
      overflow: "hidden", // Only hide overflow for page items, not arrows
      flex: "0 1 auto", // Don't grow, can shrink, auto basis
      minWidth: 0, // Allow shrinking
    }),
    [],
  );

  // Base button style
  const getButtonStyle = useCallback(
    (isActive: boolean, isDisabled: boolean): CSSProperties => {
      const baseStyle: CSSProperties = {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        width: `${ITEM_WIDTH}px`, // Fixed width for consistent sizing
        minWidth: `${ITEM_WIDTH}px`,
        height: `${ITEM_WIDTH}px`,
        padding: "0",
        border: "1px solid",
        borderRadius: "6px",
        cursor: isDisabled ? "not-allowed" : "pointer",
        transition: "border-color 0.15s ease, background-color 0.15s ease",
        outline: "none",
        fontFamily: "inherit",
        fontSize: "inherit",
        fontWeight: isActive ? 600 : 400,
        flexShrink: 0, // Don't shrink
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
    [],
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
      width: `${ITEM_WIDTH}px`, // Fixed width for consistent sizing
      minWidth: `${ITEM_WIDTH}px`,
      height: `${ITEM_WIDTH}px`,
      color: "var(--st-text-color)",
      userSelect: "none",
      flexShrink: 0, // Don't shrink
    }),
    [],
  );

  const isPrevDisabled = disabled || currentPage === 1;
  const isNextDisabled = disabled || currentPage === numPages;

  return (
    <>
      <style>{globalStyles}</style>
      <div ref={containerRef} style={outerContainerStyle}>
        <div style={innerContainerStyle}>
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

          {/* Page items wrapper - handles overflow without hiding arrows */}
          <div style={pageItemsWrapperStyle}>
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
          </div>

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
      </div>
    </>
  );
};

export default Pagination;
