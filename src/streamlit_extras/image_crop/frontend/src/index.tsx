import {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import { StrictMode } from "react";
import { createRoot, Root } from "react-dom/client";

import ImageCrop, { ImageCropDataShape, ImageCropStateShape } from "./ImageCrop";

// Handle the possibility of multiple instances of the component to keep track
// of the React roots for each component instance.
const reactRoots: WeakMap<FrontendRendererArgs["parentElement"], Root> =
  new WeakMap();

const ImageCropRoot: FrontendRenderer<ImageCropStateShape, ImageCropDataShape> =
  (args) => {
    const { data, parentElement, setStateValue } = args;

    // Get the react-root div from the parentElement that we defined in our
    // `st.components.v2.component` call in Python.
    const rootElement = parentElement.querySelector(".react-root");

    if (!rootElement) {
      throw new Error("Unexpected: React root element not found");
    }

    // Check to see if we already have a React root for this component instance.
    let reactRoot = reactRoots.get(parentElement);
    if (!reactRoot) {
      // If we don't, create a new root for the React application using the React
      // DOM API.
      // @see https://react.dev/reference/react-dom/client/createRoot
      reactRoot = createRoot(rootElement);
      reactRoots.set(parentElement, reactRoot);
    }

    // Extract data passed from Streamlit on the Python side.
    const {
      image_url,
      aspect,
      min_width,
      min_height,
      initial_crop,
      circular,
      rule_of_thirds,
      height,
      width,
      track_crop,
    } = data;

    // Render/re-render the React application into the root using the React DOM
    // API.
    reactRoot.render(
      <StrictMode>
        <ImageCrop
          setStateValue={setStateValue}
          imageUrl={image_url}
          aspect={aspect}
          minWidth={min_width}
          minHeight={min_height}
          initialCrop={initial_crop}
          circular={circular}
          ruleOfThirds={rule_of_thirds}
          height={height}
          width={width}
          trackCrop={track_crop}
        />
      </StrictMode>,
    );

    // Return a function to cleanup the React application in the Streamlit
    // component lifecycle.
    return () => {
      const reactRoot = reactRoots.get(parentElement);

      if (reactRoot) {
        reactRoot.unmount();
        reactRoots.delete(parentElement);
      }
    };
  };

export default ImageCropRoot;
