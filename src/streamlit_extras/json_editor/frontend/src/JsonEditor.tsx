import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import ReactJson, {
  InteractionProps,
  ThemeKeys,
} from "@microlink/react-json-view";
import {
  FC,
  ReactElement,
  useCallback,
  useMemo,
  useState,
  useRef,
  CSSProperties,
} from "react";

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

  // Local state to track the current data (including edits)
  // Initialize with json_data on first render
  const [currentData, setCurrentData] = useState<unknown>(() => {
    isInitialized.current = true;
    // Set initial state value on first render
    setStateValue("data", json_data);
    return json_data;
  });

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
    <div style={containerStyle}>
      <ReactJson
        src={currentData as object}
        name={rootName}
        collapsed={collapsed}
        theme={theme as ThemeKeys}
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
