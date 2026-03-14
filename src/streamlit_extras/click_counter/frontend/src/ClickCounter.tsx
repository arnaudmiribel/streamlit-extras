import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import {
  CSSProperties,
  FC,
  ReactElement,
  useCallback,
  useMemo,
  useState,
} from "react";

export type ClickCounterStateShape = {
  count: number;
};

export type ClickCounterDataShape = {
  label: string;
};

export type ClickCounterProps = Pick<
  FrontendRendererArgs<ClickCounterStateShape, ClickCounterDataShape>,
  "setStateValue"
> &
  ClickCounterDataShape;

/**
 * A simple click counter component for Streamlit.
 *
 * This component demonstrates the essential structure and patterns for
 * creating interactive Streamlit components with React, including:
 * - Accessing data sent from Python
 * - Managing component state with React hooks
 * - Communicating back to Streamlit via setStateValue()
 * - Using the Streamlit CSS Custom Properties for styling
 *
 * @param props.label - Button label passed from the Python side
 * @param props.setStateValue - Function to send state updates back to Streamlit
 * @returns The rendered component
 */
const ClickCounter: FC<ClickCounterProps> = ({
  label,
  setStateValue,
}): ReactElement => {
  // Frontend component state
  const [isFocused, setIsFocused] = useState(false);
  const [count, setCount] = useState(0);

  /**
   * Dynamic styling based on Streamlit theme and component state.
   * This demonstrates how to use the Streamlit theme for consistent styling.
   */
  const containerStyle = useMemo<CSSProperties>(
    () => ({
      display: "flex",
      alignItems: "center",
      gap: "1rem",
      fontFamily: "var(--st-font)",
      color: "var(--st-text-color)",
    }),
    [],
  );

  const buttonStyle = useMemo<CSSProperties>(() => {
    const borderColor = isFocused
      ? "var(--st-primary-color)"
      : "var(--st-gray-color)";

    return {
      backgroundColor: "var(--st-primary-color)",
      color: "var(--st-background-color)",
      border: `2px solid ${borderColor}`,
      borderRadius: "0.5rem",
      padding: "0.5rem 1rem",
      fontSize: "1rem",
      cursor: "pointer",
      transition: "all 0.2s ease",
      outline: "none",
    };
  }, [isFocused]);

  const countStyle = useMemo<CSSProperties>(
    () => ({
      fontSize: "1.5rem",
      fontWeight: "bold",
      minWidth: "3rem",
      textAlign: "center",
    }),
    [],
  );

  /**
   * Click handler for the button.
   * Demonstrates how to update component state and send data back to Streamlit.
   */
  const onClicked = useCallback((): void => {
    const newCount = count + 1;
    // Update local state
    setCount(newCount);
    // Send state value back to Streamlit (will be available in Python)
    setStateValue("count", newCount);
  }, [count, setStateValue]);

  /**
   * Focus handler for the button.
   * Updates visual state when the button receives focus.
   */
  const onFocus = useCallback((): void => {
    setIsFocused(true);
  }, []);

  /**
   * Blur handler for the button.
   * Updates visual state when the button loses focus.
   */
  const onBlur = useCallback((): void => {
    setIsFocused(false);
  }, []);

  return (
    <div style={containerStyle}>
      <button
        style={buttonStyle}
        onClick={onClicked}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        {label}
      </button>
      <span style={countStyle}>{count}</span>
    </div>
  );
};

export default ClickCounter;
