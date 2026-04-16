import { Chart, ChartConfiguration, registerables } from "chart.js";
import { useEffect, useRef, useState, useCallback } from "react";

// Register all Chart.js components
Chart.register(...registerables);

// Use a looser type for the spec to handle dynamic theming
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ChartSpec = Record<string, any>;

export interface ChartJSChartDataShape {
  spec: ChartSpec;
  height: "content" | "stretch" | number;
  theme: "streamlit" | null;
}

interface ChartJSChartProps {
  spec: ChartSpec;
  height: "content" | "stretch" | number;
  theme: "streamlit" | null;
}

// Fallback colors if CSS variables aren't available
const FALLBACK_COLORS = [
  "#FF4B4B",
  "#1C83E1",
  "#00C4B4",
  "#FA8C16",
  "#9254DE",
  "#F5222D",
  "#52C41A",
  "#FAAD14",
  "#13C2C2",
  "#EB2F96",
];

type ThemeColors = {
  textColor: string;
  backgroundColor: string;
  borderColor: string;
  fontFamily: string;
  chartColors: string[];
};

// Helper to get CSS variable from the correct element (Shadow DOM aware)
const getCSSVariable = (
  element: HTMLElement | null,
  name: string,
  fallback: string,
): string => {
  if (!element) return fallback;

  // In Shadow DOM, get computed style from the host element
  const host = (element.getRootNode() as ShadowRoot)?.host ?? element;
  const value = getComputedStyle(host as Element)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
};

// Get chart colors from Streamlit's CSS variable
const getChartColors = (element: HTMLElement | null): string[] => {
  const raw = getCSSVariable(element, "--st-chart-categorical-colors", "");
  if (raw) {
    // Split comma-separated colors and trim whitespace
    return raw.split(",").map((c) => c.trim());
  }
  return FALLBACK_COLORS;
};

// Read all theme colors from CSS variables
const getThemeColors = (element: HTMLElement | null): ThemeColors => {
  return {
    textColor: getCSSVariable(element, "--st-text-color", "#31333F"),
    backgroundColor: getCSSVariable(element, "--st-background-color", "#FFFFFF"),
    borderColor: getCSSVariable(
      element,
      "--st-border-color-light",
      "rgba(128, 128, 128, 0.2)",
    ),
    fontFamily: getCSSVariable(
      element,
      "--st-font",
      '"Source Sans Pro", sans-serif',
    ),
    chartColors: getChartColors(element),
  };
};

// Apply Streamlit theme to Chart.js configuration
const applyStreamlitTheme = (
  spec: ChartSpec,
  colors: ThemeColors,
): ChartSpec => {
  // Deep clone the spec to avoid mutating the original
  const themedSpec = JSON.parse(JSON.stringify(spec)) as ChartSpec;

  const { textColor, backgroundColor, borderColor, fontFamily, chartColors } =
    colors;

  // Apply colors to datasets if not already specified
  if (themedSpec.data?.datasets) {
    themedSpec.data.datasets = themedSpec.data.datasets.map(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (dataset: any, idx: number) => {
        const color = chartColors[idx % chartColors.length];

        // For pie/doughnut/polarArea, use array of colors for segments
        const isPieType = ["pie", "doughnut", "polarArea"].includes(
          themedSpec.type as string,
        );

        if (isPieType) {
          const dataLength =
            (dataset.data as unknown[])?.length || chartColors.length;
          return {
            ...dataset,
            backgroundColor:
              dataset.backgroundColor || chartColors.slice(0, dataLength),
            borderColor: dataset.borderColor || backgroundColor,
            borderWidth: dataset.borderWidth ?? 2,
          };
        }

        // For line/radar charts, use transparent background with solid border
        const isLineType = ["line", "radar"].includes(
          themedSpec.type as string,
        );

        if (isLineType) {
          return {
            ...dataset,
            borderColor: dataset.borderColor || color,
            backgroundColor: dataset.backgroundColor || `${color}33`, // 20% opacity
            pointBackgroundColor: dataset.pointBackgroundColor || color,
            pointBorderColor: dataset.pointBorderColor || backgroundColor,
            tension: dataset.tension ?? 0.4, // Smooth curves by default
          };
        }

        // For bar/bubble/scatter charts
        return {
          ...dataset,
          backgroundColor: dataset.backgroundColor || `${color}CC`, // 80% opacity
          borderColor: dataset.borderColor || color,
          borderWidth: dataset.borderWidth ?? 1,
        };
      },
    );
  }

  // Apply theme to options
  themedSpec.options = themedSpec.options || {};

  // Configure plugins
  themedSpec.options.plugins = themedSpec.options.plugins || {};

  // Legend styling
  themedSpec.options.plugins.legend = {
    labels: {
      color: textColor,
      font: {
        family: fontFamily,
      },
    },
    ...themedSpec.options.plugins.legend,
  };

  // Title styling
  if (themedSpec.options.plugins.title) {
    themedSpec.options.plugins.title = {
      color: textColor,
      font: {
        family: fontFamily,
        size: 14,
        weight: "bold" as const,
      },
      ...themedSpec.options.plugins.title,
    };
  }

  // Tooltip styling
  themedSpec.options.plugins.tooltip = {
    backgroundColor: backgroundColor,
    titleColor: textColor,
    bodyColor: textColor,
    borderColor: borderColor,
    borderWidth: 1,
    cornerRadius: 4,
    ...themedSpec.options.plugins.tooltip,
  };

  // Scale styling (for charts with axes)
  const hasScales = !["pie", "doughnut", "polarArea", "radar"].includes(
    themedSpec.type as string,
  );

  if (hasScales) {
    themedSpec.options.scales = themedSpec.options.scales || {};

    // X axis
    themedSpec.options.scales.x = {
      ticks: {
        color: textColor,
        font: {
          family: fontFamily,
        },
      },
      grid: {
        color: borderColor,
      },
      ...themedSpec.options.scales.x,
    };

    // Y axis
    themedSpec.options.scales.y = {
      ticks: {
        color: textColor,
        font: {
          family: fontFamily,
        },
      },
      grid: {
        color: borderColor,
      },
      ...themedSpec.options.scales.y,
    };
  }

  // Radar chart scale styling
  if (themedSpec.type === "radar") {
    themedSpec.options.scales = themedSpec.options.scales || {};
    themedSpec.options.scales.r = {
      ticks: {
        color: textColor,
        backdropColor: "transparent",
      },
      pointLabels: {
        color: textColor,
      },
      grid: {
        color: borderColor,
      },
      angleLines: {
        color: borderColor,
      },
      ...themedSpec.options.scales.r,
    };
  }

  // Polar area chart scale styling
  if (themedSpec.type === "polarArea") {
    themedSpec.options.scales = themedSpec.options.scales || {};
    themedSpec.options.scales.r = {
      ticks: {
        color: textColor,
        backdropColor: "transparent",
      },
      grid: {
        color: borderColor,
      },
      ...themedSpec.options.scales.r,
    };
  }

  return themedSpec;
};

const ChartJSChart: React.FC<ChartJSChartProps> = ({ spec, height, theme }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const [containerHeight, setContainerHeight] = useState<string | number>(
    "auto",
  );

  // Track theme colors with polling (like json_editor and sigma_graph)
  const [themeColors, setThemeColors] = useState<ThemeColors>(() => ({
    textColor: "#31333F",
    backgroundColor: "#FFFFFF",
    borderColor: "rgba(128, 128, 128, 0.2)",
    fontFamily: '"Source Sans Pro", sans-serif',
    chartColors: FALLBACK_COLORS,
  }));
  const lastThemeHash = useRef<string>("");

  // Poll for CSS variable changes (MutationObserver doesn't catch CSS custom property changes)
  useEffect(() => {
    if (theme !== "streamlit") return;
    if (!containerRef.current) return;

    const updateThemeFromCssVars = () => {
      const colors = getThemeColors(containerRef.current);

      // Only update if colors actually changed (avoid unnecessary re-renders)
      const hash = JSON.stringify(colors);
      if (hash !== lastThemeHash.current) {
        lastThemeHash.current = hash;
        setThemeColors(colors);
      }
    };

    // Initial detection
    updateThemeFromCssVars();

    // Poll for changes every 100ms
    const intervalId = setInterval(updateThemeFromCssVars, 100);

    return () => clearInterval(intervalId);
  }, [theme]);

  // Memoize the theming function
  const getThemedSpec = useCallback(() => {
    if (theme === "streamlit") {
      return applyStreamlitTheme(spec, themeColors);
    }
    return spec;
  }, [spec, theme, themeColors]);

  // Calculate container height based on height prop
  useEffect(() => {
    if (typeof height === "number") {
      setContainerHeight(height);
    } else if (height === "stretch") {
      setContainerHeight("100%");
    } else {
      // "content" - let Chart.js determine height
      setContainerHeight("auto");
    }
  }, [height]);

  // Create/update the chart
  useEffect(() => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (chartRef.current) {
      chartRef.current.destroy();
      chartRef.current = null;
    }

    // Get themed spec
    const themedSpec = getThemedSpec();

    // Determine default aspect ratio based on chart type
    // Circular charts (pie, doughnut, radar, polarArea) look best square
    // Bar/line/scatter charts look best wider
    const chartType = themedSpec.type as string;
    const isCircularChart = ["pie", "doughnut", "radar", "polarArea"].includes(
      chartType,
    );
    const defaultAspectRatio = isCircularChart ? 1.5 : 2;

    // Configure Chart.js defaults for responsive behavior
    const chartConfig = {
      ...themedSpec,
      options: {
        ...themedSpec.options,
        responsive: true,
        maintainAspectRatio: height === "content",
        // Use chart-type-appropriate aspect ratio, allow user override
        aspectRatio: themedSpec.options?.aspectRatio ?? defaultAspectRatio,
      },
    } as ChartConfiguration;

    // Create new chart
    chartRef.current = new Chart(ctx, chartConfig);

    // Cleanup function
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [getThemedSpec, height]);

  // Handle resize with ResizeObserver
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resizeObserver = new ResizeObserver(() => {
      // Chart.js needs explicit resize call when container grows
      if (chartRef.current) {
        chartRef.current.resize();
      }
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  const containerStyle: React.CSSProperties = {
    width: "100%",
    height: containerHeight,
    minHeight: height === "stretch" ? "200px" : undefined,
    position: "relative",
  };

  const canvasStyle: React.CSSProperties = {
    width: "100%",
    height: "100%",
  };

  return (
    <div ref={containerRef} style={containerStyle}>
      <canvas ref={canvasRef} style={canvasStyle} />
    </div>
  );
};

export default ChartJSChart;
