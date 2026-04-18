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
import ReactCrop, { type Crop, type PercentCrop, type PixelCrop } from "react-image-crop";
// Import CSS as raw string to render inline
import reactCropStyles from "react-image-crop/dist/ReactCrop.css?raw";

// Custom overrides for Streamlit theming
const CUSTOM_STYLES = `
.ReactCrop__crop-selection {
  border: 2px solid var(--st-primary-color, #ff4b4b) !important;
}
.ReactCrop__drag-handle {
  width: 12px !important;
  height: 12px !important;
  background-color: var(--st-primary-color, #ff4b4b) !important;
  border: 2px solid #fff !important;
}
/* Make edge handles easier to grab */
.ReactCrop .ord-n,
.ReactCrop .ord-s {
  width: 24px !important;
  height: 10px !important;
  border-radius: 4px !important;
}
.ReactCrop .ord-e,
.ReactCrop .ord-w {
  width: 10px !important;
  height: 24px !important;
  border-radius: 4px !important;
}
`;

// Combined styles to render inline
const ALL_STYLES = reactCropStyles + "\n" + CUSTOM_STYLES;

// CropBounds in the frontend represents react-image-crop percent values (0-100).
// Note: Python API uses normalized 0-1 values; conversion happens at the boundary.
export type CropBounds = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type ImageCropStateShape = {
  crop: CropBounds | null;
};

export type ImageCropDataShape = {
  image_url: string;
  aspect: number | null;
  min_width: number;
  min_height: number;
  initial_crop: CropBounds | null;
  circular: boolean;
  rule_of_thirds: boolean;
  height: "content" | number;
  width: "content" | "stretch" | number;
  track_crop: boolean;
};

export type ImageCropProps = Pick<
  FrontendRendererArgs<ImageCropStateShape, ImageCropDataShape>,
  "setStateValue"
> & {
  imageUrl: string;
  aspect: number | null;
  minWidth: number;
  minHeight: number;
  initialCrop: CropBounds | null;
  circular: boolean;
  ruleOfThirds: boolean;
  height: "content" | number;
  width: "content" | "stretch" | number;
  trackCrop: boolean;
};

// Typed global Window interface for Streamlit
declare global {
  interface Window {
    __streamlit?: {
      DOWNLOAD_ASSETS_BASE_URL?: string;
    };
  }
}

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
    if (window.__streamlit?.DOWNLOAD_ASSETS_BASE_URL) {
      baseUrl = window.__streamlit.DOWNLOAD_ASSETS_BASE_URL;
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

/**
 * Convert CropBounds to react-image-crop's PercentCrop format.
 */
function cropBoundsToPercentCrop(bounds: CropBounds): PercentCrop {
  return {
    unit: "%",
    x: bounds.x,
    y: bounds.y,
    width: bounds.width,
    height: bounds.height,
  };
}

/**
 * Normalize a percent crop value to ensure it's a valid number in [0, 100].
 */
function normalizePercentValue(value: number | undefined): number {
  const normalized =
    typeof value === "number" && Number.isFinite(value) ? value : 0;
  return Math.min(100, Math.max(0, normalized));
}

/**
 * Convert react-image-crop's PercentCrop to CropBounds with normalization.
 */
function percentCropToCropBounds(crop: PercentCrop): CropBounds {
  return {
    x: normalizePercentValue(crop.x),
    y: normalizePercentValue(crop.y),
    width: normalizePercentValue(crop.width),
    height: normalizePercentValue(crop.height),
  };
}

/**
 * Image cropping component using react-image-crop.
 */
const ImageCrop: FC<ImageCropProps> = ({
  imageUrl,
  aspect,
  minWidth,
  minHeight,
  initialCrop,
  circular,
  ruleOfThirds,
  height,
  width,
  trackCrop,
  setStateValue,
}): ReactElement => {
  const [crop, setCrop] = useState<Crop | undefined>(() =>
    initialCrop ? cropBoundsToPercentCrop(initialCrop) : undefined,
  );
  const [imageHeight, setImageHeight] = useState<number | null>(
    typeof height === "number" ? height : null,
  );
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Refs for debounced crop updates
  const pendingCropRef = useRef<CropBounds | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastCommittedCropRef = useRef<CropBounds | null>(initialCrop);

  // Track image aspect ratio for crop adjustments
  const [imageAspectRatio, setImageAspectRatio] = useState<number | null>(null);

  // Debounce delay in milliseconds
  const DEBOUNCE_DELAY = 150;

  // Resolve media URL
  const resolvedImageUrl = useMemo(
    () => resolveMediaUrl(imageUrl),
    [imageUrl],
  );

  // Load image to get its aspect ratio
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      if (img.width > 0 && img.height > 0) {
        setImageAspectRatio(img.width / img.height);
      }
    };
    img.src = resolvedImageUrl;
    return () => {
      img.onload = null;
    };
  }, [resolvedImageUrl]);

  // Sync crop when initialCrop, aspect, or image dimensions change
  useEffect(() => {
    if (!initialCrop) {
      setCrop(undefined);
      lastCommittedCropRef.current = null;
      return;
    }

    let cropToSet = cropBoundsToPercentCrop(initialCrop);

    // If there's an aspect constraint and we know the image dimensions, adjust the crop
    if (aspect && imageAspectRatio) {
      const currentWidth = cropToSet.width ?? 0;
      const currentHeight = cropToSet.height ?? 0;
      const currentX = cropToSet.x ?? 0;
      const currentY = cropToSet.y ?? 0;

      if (currentWidth > 0 && currentHeight > 0) {
        // In percent space, the aspect ratio that produces a visually correct
        // crop is: desiredAspect / imageAspect
        // For a square (aspect=1) on a 2:1 image, we need width%/height% = 0.5
        const targetPercentAspect = aspect / imageAspectRatio;
        const currentPercentAspect = currentWidth / currentHeight;

        // Only adjust if aspect doesn't match (with tolerance)
        if (Math.abs(currentPercentAspect - targetPercentAspect) >= 0.01) {
          let newWidth = currentWidth;
          let newHeight = currentHeight;

          if (currentPercentAspect > targetPercentAspect) {
            // Current crop is wider than target - reduce width
            newWidth = currentHeight * targetPercentAspect;
          } else {
            // Current crop is taller than target - reduce height
            newHeight = currentWidth / targetPercentAspect;
          }

          // Adjust position to keep the crop centered
          const centerX = currentX + currentWidth / 2;
          const centerY = currentY + currentHeight / 2;
          let newX = centerX - newWidth / 2;
          let newY = centerY - newHeight / 2;

          // Clamp to image bounds (0-100%)
          if (newX < 0) {
            newX = 0;
          } else if (newX + newWidth > 100) {
            newX = 100 - newWidth;
          }
          if (newY < 0) {
            newY = 0;
          } else if (newY + newHeight > 100) {
            newY = 100 - newHeight;
          }

          cropToSet = {
            unit: "%",
            x: newX,
            y: newY,
            width: newWidth,
            height: newHeight,
          };
        }
      }
    }

    setCrop(cropToSet);
    const cropBounds = percentCropToCropBounds(cropToSet);
    lastCommittedCropRef.current = cropBounds;

    // Notify Streamlit of the adjusted crop
    if (trackCrop) {
      setStateValue("crop", cropBounds);
    }
  }, [initialCrop, aspect, imageAspectRatio, trackCrop, setStateValue]);

  // Cleanup for debounce timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current !== null) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  // Clear pending debounce timer when tracking is disabled
  useEffect(() => {
    if (!trackCrop && debounceTimerRef.current !== null) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }
  }, [trackCrop]);

  // Calculate height based on image aspect ratio if height is "content"
  useEffect(() => {
    if (typeof height === "number") {
      setImageHeight(height);
      return;
    }

    let isMounted = true;
    let aspectRatio: number | null = null;
    const container = containerRef.current;

    const updateImageHeight = () => {
      if (!isMounted || !containerRef.current || aspectRatio === null) {
        return;
      }
      const containerWidth = containerRef.current.clientWidth;
      setImageHeight(Math.round(containerWidth * aspectRatio));
    };

    // Load image to get dimensions
    const img = new Image();
    img.onload = () => {
      if (!isMounted || img.width === 0) {
        return;
      }
      aspectRatio = img.height / img.width;
      updateImageHeight();
    };
    img.src = resolvedImageUrl;

    // Observe container resize to update height
    let resizeObserver: ResizeObserver | null = null;
    if (container) {
      resizeObserver = new ResizeObserver(() => {
        updateImageHeight();
      });
      resizeObserver.observe(container);
    }

    return () => {
      isMounted = false;
      img.onload = null;
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, [height, resolvedImageUrl]);

  // Handle crop change with debouncing to prevent rapid reruns
  const handleCropChange = useCallback(
    (_pixelCrop: PixelCrop, percentCrop: PercentCrop) => {
      setCrop(percentCrop);

      // Only send state updates if tracking is enabled
      if (!trackCrop) {
        return;
      }

      const cropBounds = percentCropToCropBounds(percentCrop);
      pendingCropRef.current = cropBounds;

      // Debounce state updates to avoid excessive reruns
      if (debounceTimerRef.current !== null) {
        clearTimeout(debounceTimerRef.current);
      }

      debounceTimerRef.current = setTimeout(() => {
        debounceTimerRef.current = null;

        if (pendingCropRef.current !== null) {
          const pending = pendingCropRef.current;
          const last = lastCommittedCropRef.current;

          // Only update if crop has changed
          if (
            !last ||
            pending.x !== last.x ||
            pending.y !== last.y ||
            pending.width !== last.width ||
            pending.height !== last.height
          ) {
            lastCommittedCropRef.current = pending;
            setStateValue("crop", pending);
          }
        }
      }, DEBOUNCE_DELAY);
    },
    [setStateValue, trackCrop],
  );

  // Handle crop complete (final update after drag ends)
  const handleCropComplete = useCallback(
    (_pixelCrop: PixelCrop, percentCrop: PercentCrop) => {
      if (!trackCrop) {
        return;
      }

      // Clear any pending debounce and commit immediately
      if (debounceTimerRef.current !== null) {
        clearTimeout(debounceTimerRef.current);
        debounceTimerRef.current = null;
      }

      const cropBounds = percentCropToCropBounds(percentCrop);
      const last = lastCommittedCropRef.current;

      // Skip if crop hasn't changed or has zero dimensions
      if (
        cropBounds.width === 0 ||
        cropBounds.height === 0 ||
        (last &&
          cropBounds.x === last.x &&
          cropBounds.y === last.y &&
          cropBounds.width === last.width &&
          cropBounds.height === last.height)
      ) {
        return;
      }

      lastCommittedCropRef.current = cropBounds;
      setStateValue("crop", cropBounds);
    },
    [setStateValue, trackCrop],
  );

  // Container styles
  const containerStyle = useMemo<CSSProperties>(() => {
    const style: CSSProperties = {
      position: "relative",
      overflow: "hidden",
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

  return (
    <div ref={containerRef} style={containerStyle}>
      <style>{ALL_STYLES}</style>
      <ReactCrop
        crop={crop}
        onChange={handleCropChange}
        onComplete={handleCropComplete}
        aspect={aspect ?? undefined}
        minWidth={minWidth}
        minHeight={minHeight}
        circularCrop={circular}
        ruleOfThirds={ruleOfThirds}
        style={{
          width: "100%",
          height: imageHeight !== null ? `${imageHeight}px` : "auto",
        }}
      >
        <img
          ref={imgRef}
          src={resolvedImageUrl}
          alt="Crop source"
          style={{
            display: "block",
            maxWidth: "100%",
            height: imageHeight !== null ? `${imageHeight}px` : "auto",
            objectFit: "contain",
          }}
        />
      </ReactCrop>
    </div>
  );
};

export default ImageCrop;
