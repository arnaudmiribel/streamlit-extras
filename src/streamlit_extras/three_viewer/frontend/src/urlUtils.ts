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
  // Ensure we're running in a browser-like environment
  if (typeof window === "undefined") {
    return null;
  }

  // Check for explicitly configured download assets base URL
  if (window.__streamlit?.DOWNLOAD_ASSETS_BASE_URL) {
    return window.__streamlit.DOWNLOAD_ASSETS_BASE_URL;
  }

  // Fall back to current window location
  if (window.location) {
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

    // If the path doesn't end with /, we need to determine the base path.
    // We remove the last segment only if there are multiple segments,
    // otherwise we preserve it (for single-segment subpaths like /foo).
    if (!basePath.endsWith("/")) {
      const lastSlash = basePath.lastIndexOf("/");
      // Only strip the last segment if it's not the root
      // and there's more than one segment (lastSlash > 0)
      if (lastSlash > 0) {
        basePath = basePath.substring(0, lastSlash);
      } else {
        // Single segment like "/foo" - keep the full path as base
        // (the file is served at the root of that subpath)
        basePath = "";
      }
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
