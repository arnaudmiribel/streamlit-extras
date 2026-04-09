import { FC, useEffect, useRef } from "react";
import { FrontendRendererArgs } from "@streamlit/component-v2-lib";

// Type definitions
export interface AnywidgetStateShape {
  [key: string]: unknown;
}

export interface AnywidgetDataShape {
  esm: string;
  css: string | null;
  traits: Record<string, unknown>;
}

interface AnywidgetContainerProps {
  esm: string;
  css: string | null;
  traits: Record<string, unknown>;
  setStateValue: FrontendRendererArgs<
    AnywidgetStateShape,
    AnywidgetDataShape
  >["setStateValue"];
}

// Anywidget model interface
interface AnywidgetModel {
  get: (key: string) => unknown;
  set: (key: string, value: unknown) => void;
  save_changes: () => void;
  on: (event: string, callback: () => void) => void;
  off: (event: string, callback: () => void) => void;
  send: (content: unknown, callbacks?: unknown, buffers?: unknown) => void;
}

// Widget instance stored in ref
interface WidgetInstance {
  model: AnywidgetModel;
  currentTraits: Record<string, unknown>;
  changeCallbacks: Record<string, Array<() => void>>;
  messageCallbacks: Array<(msg: unknown, buffers?: unknown) => void>;
  cleanup: (() => void) | null;
  messageCounter: number;
}

// CSS injection cache (module-level to persist across renders)
const injectedCss = new Set<string>();

const AnywidgetContainer: FC<AnywidgetContainerProps> = ({
  esm,
  css,
  traits,
  setStateValue,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const instanceRef = useRef<WidgetInstance | null>(null);
  const isInitializedRef = useRef(false);
  // Use refs for stable references to avoid re-initialization
  const setStateValueRef = useRef(setStateValue);
  const traitsRef = useRef(traits);

  // Keep refs up to date
  setStateValueRef.current = setStateValue;
  traitsRef.current = traits;

  // Inject CSS (only once per unique CSS content)
  useEffect(() => {
    if (css && typeof css === "string") {
      const cssHash = `anywidget-${css.length}-${css.slice(0, 50)}`;
      if (!injectedCss.has(cssHash)) {
        const style = document.createElement("style");
        style.textContent = css;
        document.head.appendChild(style);
        injectedCss.add(cssHash);
      }
    }
  }, [css]);

  // Initialize widget (runs once on mount, only depends on esm)
  useEffect(() => {
    if (!containerRef.current || isInitializedRef.current) {
      return;
    }

    isInitializedRef.current = true;
    const el = containerRef.current;

    // Create model adapter (uses refs for stable access to latest values)
    const pendingChanges: Record<string, unknown> = {};
    const currentTraits: Record<string, unknown> = { ...traitsRef.current };
    const changeCallbacks: Record<string, Array<() => void>> = {};
    const messageCallbacks: Array<(msg: unknown, buffers?: unknown) => void> =
      [];
    let messageCounter = 0;

    const model: AnywidgetModel = {
      get(key: string) {
        return key in pendingChanges ? pendingChanges[key] : currentTraits[key];
      },
      set(key: string, value: unknown) {
        const oldValue = currentTraits[key];
        pendingChanges[key] = value;
        currentTraits[key] = value;

        // Fire change callbacks immediately when value changes
        if (oldValue !== value) {
          const callbacks = changeCallbacks[`change:${key}`] || [];
          callbacks.forEach((cb) => {
            try {
              cb();
            } catch (e) {
              console.error("Callback error:", e);
            }
          });
          // Also fire general change callback
          const generalCallbacks = changeCallbacks["change"] || [];
          generalCallbacks.forEach((cb) => {
            try {
              cb();
            } catch (e) {
              console.error("Callback error:", e);
            }
          });
        }
      },
      save_changes() {
        for (const [key, value] of Object.entries(pendingChanges)) {
          setStateValueRef.current(key, value);
        }
        // Clear pending changes
        Object.keys(pendingChanges).forEach((k) => delete pendingChanges[k]);
      },
      on(event: string, callback: () => void) {
        // Handle special "msg:custom" event for receiving messages from Python
        if (event === "msg:custom") {
          messageCallbacks.push(
            callback as unknown as (msg: unknown, buffers?: unknown) => void,
          );
          return;
        }
        if (!changeCallbacks[event]) {
          changeCallbacks[event] = [];
        }
        changeCallbacks[event].push(callback);
      },
      off(event: string, callback: () => void) {
        if (event === "msg:custom") {
          const idx = messageCallbacks.indexOf(
            callback as unknown as (msg: unknown, buffers?: unknown) => void,
          );
          if (idx !== -1) messageCallbacks.splice(idx, 1);
          return;
        }
        if (changeCallbacks[event]) {
          changeCallbacks[event] = changeCallbacks[event].filter(
            (cb) => cb !== callback,
          );
        }
      },
      send(content: unknown, _callbacks?: unknown, _buffers?: unknown) {
        // Send message to Python via state
        // Use a unique message ID to ensure each message triggers a state change
        messageCounter++;
        setStateValueRef.current("_anywidget_msg", {
          id: messageCounter,
          content: content,
          timestamp: Date.now(),
        });
      },
    };

    // Store instance data
    instanceRef.current = {
      model,
      currentTraits,
      changeCallbacks,
      messageCallbacks,
      cleanup: null,
      messageCounter,
    };

    // Execute ESM module
    const initWidget = async () => {
      try {
        // Convert ESM to blob URL for dynamic import
        const blob = new Blob([esm], { type: "text/javascript" });
        const url = URL.createObjectURL(blob);

        let widgetModule;
        try {
          widgetModule = await import(/* @vite-ignore */ url);
        } finally {
          URL.revokeObjectURL(url);
        }

        const widgetDef = widgetModule.default || widgetModule;
        const cleanupFns: Array<() => void> = [];

        // Call initialize lifecycle hook if present
        if (
          widgetDef.initialize &&
          typeof widgetDef.initialize === "function"
        ) {
          const initCleanup = widgetDef.initialize({ model });
          if (typeof initCleanup === "function") {
            cleanupFns.push(initCleanup);
          }
        }

        // Call render function
        if (widgetDef.render && typeof widgetDef.render === "function") {
          const renderCleanup = widgetDef.render({ model, el });
          if (typeof renderCleanup === "function") {
            cleanupFns.push(renderCleanup);
          }
        } else if (typeof widgetDef === "function") {
          // Handle direct render function export
          const renderCleanup = widgetDef({ model, el });
          if (typeof renderCleanup === "function") {
            cleanupFns.push(renderCleanup);
          }
        }

        // Store cleanup function
        if (instanceRef.current) {
          instanceRef.current.cleanup =
            cleanupFns.length > 0
              ? () => {
                  cleanupFns.forEach((fn) => {
                    try {
                      fn();
                    } catch (e) {
                      console.error("Cleanup error:", e);
                    }
                  });
                }
              : null;
        }
      } catch (err) {
        console.error("Anywidget error:", err);
        el.innerHTML = `
          <div style="color: var(--st-error-text-color, #ff4b4b);
                      background: var(--st-error-background-color, #fff0f0);
                      padding: 1rem;
                      border-radius: 0.5rem;
                      border: 1px solid var(--st-error-text-color, #ff4b4b);
                      font-family: var(--st-font-family-sans-serif);">
            <strong>Widget Error:</strong> ${err instanceof Error ? err.message : String(err)}
          </div>
        `;
      }
    };

    initWidget();

    // Cleanup on unmount
    return () => {
      if (instanceRef.current?.cleanup) {
        instanceRef.current.cleanup();
      }
      instanceRef.current = null;
      isInitializedRef.current = false;
    };
    // Only re-initialize if ESM changes (not on trait changes)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [esm]);

  // Update traits when they change (after initialization)
  useEffect(() => {
    if (!instanceRef.current || !isInitializedRef.current) {
      return;
    }

    const { currentTraits, changeCallbacks, messageCallbacks } =
      instanceRef.current;

    // Check for incoming messages from Python
    const incomingMsg = traits["_anywidget_msg_from_python"];
    if (
      incomingMsg &&
      typeof incomingMsg === "object" &&
      incomingMsg !== null
    ) {
      const msg = incomingMsg as { id: number; content: unknown };
      const lastProcessedId = (currentTraits["_last_processed_msg_id"] ||
        0) as number;
      if (msg.id > lastProcessedId) {
        currentTraits["_last_processed_msg_id"] = msg.id;
        // Fire message callbacks
        messageCallbacks.forEach((cb) => {
          try {
            cb(msg.content);
          } catch (e) {
            console.error("Message callback error:", e);
          }
        });
      }
    }

    // Update traits and fire change callbacks
    let anyTraitChanged = false;
    for (const [key, newValue] of Object.entries(traits)) {
      // Skip internal message fields
      if (key.startsWith("_anywidget_msg")) continue;

      const oldValue = currentTraits[key];
      if (oldValue !== newValue) {
        anyTraitChanged = true;
        currentTraits[key] = newValue;
        // Fire property-specific change callbacks
        const callbacks = changeCallbacks[`change:${key}`] || [];
        callbacks.forEach((cb) => {
          try {
            cb();
          } catch (e) {
            console.error("Callback error:", e);
          }
        });
      }
    }

    // Fire general change callbacks only if at least one trait changed
    if (anyTraitChanged) {
      const generalCallbacks = changeCallbacks["change"] || [];
      generalCallbacks.forEach((cb) => {
        try {
          cb();
        } catch (e) {
          console.error("Callback error:", e);
        }
      });
    }
  }, [traits]);

  return (
    <div
      ref={containerRef}
      className="anywidget-container"
      style={{
        width: "100%",
        minHeight: 0,
        overflow: "visible",
      }}
    />
  );
};

export default AnywidgetContainer;
