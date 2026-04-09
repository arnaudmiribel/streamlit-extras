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
import {
  ReactCompareSlider,
  ReactCompareSliderImage,
} from "react-compare-slider";

export type ImageCompareSliderStateShape = {
  position: number;
};

export type ImageCompareSliderDataShape = {
  image1_url: string;
  image2_url: string;
  label1: string;
  label2: string;
  portrait: boolean;
  height: "content" | number;
  width: "content" | "stretch" | number;
  initial_position: number;
};

export type ImageCompareSliderProps = Pick<
  FrontendRendererArgs<ImageCompareSliderStateShape, ImageCompareSliderDataShape>,
  "setStateValue"
> & {
  initialPosition: number;
  image1Url: string;
  image2Url: string;
  label1: string;
  label2: string;
  portrait: boolean;
  height: "content" | number;
  width: "content" | "stretch" | number;
};

/**
 * Resolve media URLs to absolute URLs.
 * Handles /media/ paths from Streamlit's media file storage.
 */
function resolveMediaUrl(url: string): string {
  if (!url) return url;

  // Already absolute URL or data URL
  if (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url.startsWith("data:")
  ) {
    return url;
  }

  // Handle /media/ paths
  if (url.startsWith("/media/") || url.startsWith("media/")) {
    const normalizedUrl = url.startsWith("/") ? url : "/" + url;

    // Try to get base URL from Streamlit config or window location
    let baseUrl = "";
    const streamlit = (window as unknown as { __streamlit?: { DOWNLOAD_ASSETS_BASE_URL?: string } }).__streamlit;
    if (streamlit?.DOWNLOAD_ASSETS_BASE_URL) {
      baseUrl = streamlit.DOWNLOAD_ASSETS_BASE_URL;
    } else if (window.location) {
      baseUrl = window.location.origin + window.location.pathname;
    }

    if (baseUrl) {
      try {
        const parsed = new URL(baseUrl);
        let basePath = parsed.pathname;
        if (!basePath.endsWith("/")) {
          const lastSlash = basePath.lastIndexOf("/");
          basePath = lastSlash > 0 ? basePath.substring(0, lastSlash) : "";
        } else {
          basePath = basePath.slice(0, -1);
        }
        return parsed.origin + (basePath + normalizedUrl).replace(/\/+/g, "/");
      } catch {
        return url;
      }
    }
  }

  return url;
}

// Label component for image overlays
const ImageLabel: FC<{
  label: string;
  position: "left" | "right" | "top" | "bottom";
}> = ({ label, position }) => {
  if (!label) return null;

  const style: CSSProperties = {
    position: "absolute",
    padding: "4px 8px",
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    color: "white",
    fontSize: "12px",
    fontWeight: 500,
    borderRadius: "4px",
    pointerEvents: "none",
    zIndex: 10,
    ...(position === "left" && { top: "8px", left: "8px" }),
    ...(position === "right" && { top: "8px", right: "8px" }),
    ...(position === "top" && { top: "8px", left: "8px" }),
    ...(position === "bottom" && { bottom: "8px", left: "8px" }),
  };

  return <div style={style}>{label}</div>;
};

/**
 * Image comparison slider component using react-compare-slider.
 */
const ImageCompareSlider: FC<ImageCompareSliderProps> = ({
  initialPosition,
  image1Url,
  image2Url,
  label1,
  label2,
  portrait,
  height,
  width,
  setStateValue,
}): ReactElement => {
  const [position, setPosition] = useState(initialPosition);
  const [imageHeight, setImageHeight] = useState<number | null>(
    typeof height === "number" ? height : null
  );
  const containerRef = useRef<HTMLDivElement>(null);

  // Resolve media URLs
  const resolvedImage1Url = useMemo(
    () => resolveMediaUrl(image1Url),
    [image1Url],
  );
  const resolvedImage2Url = useMemo(
    () => resolveMediaUrl(image2Url),
    [image2Url],
  );

  // Sync position when initialPosition changes (e.g., when position param changes on rerun)
  useEffect(() => {
    setPosition(initialPosition);
  }, [initialPosition]);

  // Calculate height based on image aspect ratio if height is "content"
  useEffect(() => {
    if (typeof height === "number") {
      setImageHeight(height);
      return;
    }

    // Load image to get dimensions
    const img = new Image();
    img.onload = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const aspectRatio = img.height / img.width;
        setImageHeight(Math.round(containerWidth * aspectRatio));
      }
    };
    img.src = resolvedImage1Url;
  }, [height, resolvedImage1Url]);

  // Handle position change
  const handlePositionChange = useCallback(
    (newPosition: number) => {
      const roundedPosition = Math.round(newPosition);
      setPosition(roundedPosition);
      setStateValue("position", roundedPosition);
    },
    [setStateValue],
  );

  // Container styles
  const containerStyle = useMemo<CSSProperties>(() => {
    const style: CSSProperties = {
      position: "relative",
      overflow: "hidden",
      borderRadius: "4px",
    };

    if (width === "stretch") {
      style.width = "100%";
    } else if (typeof width === "number") {
      style.width = `${width}px`;
    } else {
      style.width = "fit-content";
    }

    if (imageHeight !== null) {
      style.height = `${imageHeight}px`;
    }

    return style;
  }, [width, imageHeight]);

  // Custom handle styles
  const handleStyle: CSSProperties = {
    width: portrait ? "100%" : "3px",
    height: portrait ? "3px" : "100%",
    backgroundColor: "var(--st-primary-color, #ff4b4b)",
    boxShadow: "0 0 4px rgba(0, 0, 0, 0.3)",
  };

  // Custom button (circle on the handle)
  const buttonStyle: CSSProperties = {
    position: "absolute",
    top: portrait ? "-12px" : "50%",
    left: portrait ? "50%" : "-12px",
    transform: portrait ? "translateX(-50%)" : "translateY(-50%)",
    width: "24px",
    height: "24px",
    borderRadius: "50%",
    backgroundColor: "var(--st-primary-color, #ff4b4b)",
    border: "2px solid white",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.3)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: portrait ? "ns-resize" : "ew-resize",
  };

  // Arrow indicators on the button
  const arrowsStyle: CSSProperties = {
    display: "flex",
    flexDirection: portrait ? "column" : "row",
    alignItems: "center",
    justifyContent: "center",
    gap: "1px",
    color: "white",
  };

  // SVG arrow component for consistent rendering
  const Arrow: FC<{ direction: "left" | "right" | "up" | "down" }> = ({ direction }) => {
    const rotation = {
      left: 180,
      right: 0,
      up: -90,
      down: 90,
    }[direction];

    return (
      <svg
        width="8"
        height="8"
        viewBox="0 0 8 8"
        fill="none"
        style={{ transform: `rotate(${rotation}deg)` }}
      >
        <path
          d="M2 1L6 4L2 7"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  };

  // Custom handle component
  const CustomHandle = (
    <div style={{ ...handleStyle, position: "relative" }}>
      <div style={buttonStyle}>
        <div style={arrowsStyle}>
          <Arrow direction={portrait ? "up" : "left"} />
          <Arrow direction={portrait ? "down" : "right"} />
        </div>
      </div>
    </div>
  );

  return (
    <div ref={containerRef} style={containerStyle}>
      <ReactCompareSlider
        itemOne={
          <>
            <ReactCompareSliderImage
              src={resolvedImage1Url}
              alt={label1 || "Image 1"}
              style={{ objectFit: "cover", width: "100%", height: "100%" }}
            />
            <ImageLabel
              label={label1}
              position={portrait ? "top" : "left"}
            />
          </>
        }
        itemTwo={
          <>
            <ReactCompareSliderImage
              src={resolvedImage2Url}
              alt={label2 || "Image 2"}
              style={{ objectFit: "cover", width: "100%", height: "100%" }}
            />
            <ImageLabel
              label={label2}
              position={portrait ? "bottom" : "right"}
            />
          </>
        }
        handle={CustomHandle}
        position={position}
        onPositionChange={handlePositionChange}
        portrait={portrait}
        style={{
          width: "100%",
          height: imageHeight !== null ? `${imageHeight}px` : "auto",
        }}
      />
    </div>
  );
};

export default ImageCompareSlider;
