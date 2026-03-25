/**
 * URL utilities for handling Streamlit media URLs.
 * Based on streamlit-pdf's urlUtils.ts
 */

const BASE_MEDIA_PATH = "/media/";

declare global {
  interface Window {
    __streamlit?: {
      DOWNLOAD_ASSETS_BASE_URL?: string;
    };
  }
}

/**
 * Get the Streamlit base URL from the window object or current location.
 */
export function getStreamlitUrl(): string | null {
  // Check for explicitly configured download assets base URL
  if (window.__streamlit?.DOWNLOAD_ASSETS_BASE_URL) {
    return window.__streamlit.DOWNLOAD_ASSETS_BASE_URL;
  }

  // Fall back to current window location
  if (typeof window !== "undefined" && window.location) {
    return window.location.origin + window.location.pathname;
  }

  return null;
}

/**
 * Merge a file URL with the Streamlit base URL.
 * Handles media paths that start with /media/ by prepending the app's base path.
 */
export function mergeFileUrlWithStreamlitUrl(
  fileUrl: string | undefined,
): string | undefined {
  if (!fileUrl) {
    return undefined;
  }

  // If it's already an absolute URL (http/https), return as-is
  if (fileUrl.startsWith("http://") || fileUrl.startsWith("https://")) {
    return fileUrl;
  }

  // Normalize leading slash
  const normalizedUrl = fileUrl.startsWith("/") ? fileUrl : "/" + fileUrl;

  // Only process media paths
  if (!normalizedUrl.startsWith(BASE_MEDIA_PATH)) {
    return fileUrl;
  }

  const streamlitUrl = getStreamlitUrl();
  if (!streamlitUrl) {
    return fileUrl;
  }

  try {
    const url = new URL(streamlitUrl);
    const origin = url.origin;
    let basePath = url.pathname;

    // If the path doesn't end with /, remove the last segment (likely the app file)
    if (!basePath.endsWith("/")) {
      const lastSlash = basePath.lastIndexOf("/");
      basePath = lastSlash > 0 ? basePath.substring(0, lastSlash) : "";
    } else {
      // Remove trailing slash
      basePath = basePath.slice(0, -1);
    }

    // Collapse any double slashes and construct the full URL
    const fullPath = (basePath + normalizedUrl).replace(/\/+/g, "/");
    return `${origin}${fullPath}`;
  } catch {
    return fileUrl;
  }
}
