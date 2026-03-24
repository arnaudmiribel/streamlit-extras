import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import ReactJson, {
  InteractionProps,
  ThemeKeys,
} from "@microlink/react-json-view";
import Color from "color";
import {
  FC,
  ReactElement,
  useCallback,
  useMemo,
  useState,
  useRef,
  useEffect,
  CSSProperties,
} from "react";

/**
 * Determine if a background color is "light" based on luminosity.
 * Uses the Color library which handles any CSS color format.
 */
function hasLightBackgroundColor(backgroundColor: string): boolean {
  try {
    const color = Color(backgroundColor);
    // luminosity() returns 0-1 scale using WCAG relative luminance
    return color.luminosity() > 0.5;
  } catch {
    // Default to light if we can't parse the color
    return true;
  }
}

export type JsonEditorStateShape = {
  data: unknown;
};

export type JsonEditorDataShape = {
  json_data: unknown;
  name: string | null | false;
  collapsed: boolean | number;
  theme: string;
  display_data_types: boolean;
  display_object_size: boolean;
  enable_clipboard: boolean;
  sort_keys: boolean;
  editable: boolean;
};

export type JsonEditorProps = Pick<
  FrontendRendererArgs<JsonEditorStateShape, JsonEditorDataShape>,
  "setStateValue"
> &
  JsonEditorDataShape;

/**
 * A JSON editor component for Streamlit using react-json-view.
 *
 * This component provides:
 * - Collapsible tree view of JSON data
 * - Optional editing (add/edit/delete)
 * - Theming support
 * - Clipboard functionality
 *
 * @param props Component props
 * @returns The rendered component
 */
const JsonEditor: FC<JsonEditorProps> = ({
  json_data,
  name,
  collapsed,
  theme,
  display_data_types,
  display_object_size,
  enable_clipboard,
  sort_keys,
  editable,
  setStateValue,
}): ReactElement => {
  // Track if we've initialized to avoid resetting user edits
  const isInitialized = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Local state to track the current data (including edits)
  // Initialize with json_data on first render
  const [currentData, setCurrentData] = useState<unknown>(() => {
    isInitialized.current = true;
    // Set initial state value on first render
    setStateValue("data", json_data);
    return json_data;
  });

  // Auto-detect theme based on background color
  const [detectedTheme, setDetectedTheme] = useState<ThemeKeys>("rjv-default");
  const lastBackgroundColor = useRef<string>("");

  useEffect(() => {
    if (!containerRef.current) return;

    // Get the host element (shadow root host) or fall back to container
    const root = containerRef.current.getRootNode() as ShadowRoot;
    const host = root?.host ?? containerRef.current;

    // Function to detect and update theme based on background color
    const updateThemeFromBackground = () => {
      const backgroundColor = getComputedStyle(host)
        .getPropertyValue("--st-background-color")
        .trim();

      // Only update if the background color actually changed
      if (backgroundColor && backgroundColor !== lastBackgroundColor.current) {
        lastBackgroundColor.current = backgroundColor;
        const isLight = hasLightBackgroundColor(backgroundColor);
        setDetectedTheme(isLight ? "rjv-default" : "monokai");
      }
    };

    // Initial detection
    updateThemeFromBackground();

    // Poll for CSS variable changes since MutationObserver doesn't catch
    // inherited/cascading CSS custom property changes
    const intervalId = setInterval(updateThemeFromBackground, 100);

    return () => clearInterval(intervalId);
  }, []);

  // Use provided theme if specified, otherwise use auto-detected theme
  const effectiveTheme = theme || detectedTheme;

  const containerStyle = useMemo<CSSProperties>(
    () => ({
      fontFamily: "var(--st-font)",
      fontSize: "0.875rem",
      lineHeight: 1.5,
    }),
    [],
  );

  /**
   * Handler for JSON edits (value changes).
   */
  const onEdit = useCallback(
    (edit: InteractionProps) => {
      setCurrentData(edit.updated_src);
      setStateValue("data", edit.updated_src);
      return true;
    },
    [setStateValue],
  );

  /**
   * Handler for adding new keys/values.
   */
  const onAdd = useCallback(
    (add: InteractionProps) => {
      setCurrentData(add.updated_src);
      setStateValue("data", add.updated_src);
      return true;
    },
    [setStateValue],
  );

  /**
   * Handler for deleting keys/values.
   */
  const onDelete = useCallback(
    (del: InteractionProps) => {
      setCurrentData(del.updated_src);
      setStateValue("data", del.updated_src);
      return true;
    },
    [setStateValue],
  );

  // Determine the name prop - react-json-view uses false to hide the root name
  const rootName = name === null ? false : name;

  return (
    <div ref={containerRef} style={containerStyle}>
      <ReactJson
        src={currentData as object}
        name={rootName}
        collapsed={collapsed}
        theme={effectiveTheme as ThemeKeys}
        displayDataTypes={display_data_types}
        displayObjectSize={display_object_size}
        enableClipboard={enable_clipboard}
        sortKeys={sort_keys}
        onEdit={editable ? onEdit : false}
        onAdd={editable ? onAdd : false}
        onDelete={editable ? onDelete : false}
        style={{
          backgroundColor: "transparent",
          fontFamily: "var(--st-code-font)",
        }}
      />
    </div>
  );
};

export default JsonEditor;
