/**
 * Three.js 3D model viewer component for Streamlit.
 */

import { CSSProperties, FC, ReactElement, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";
import { FBXLoader } from "three/addons/loaders/FBXLoader.js";

import { mergeFileUrlWithStreamlitUrl } from "./urlUtils";

export type ThreeViewerDataShape = {
  url: string;
  format: string;
  height: number;
};

export type ThreeViewerProps = {
  url: string;
  format: string;
  height: number;
};

type LoadingState = "loading" | "loaded" | "error";

/**
 * Dispose of a Three.js object and all its children, releasing GPU resources.
 */
function disposeObject(object: THREE.Object3D): void {
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      // Dispose geometry
      if (child.geometry) {
        child.geometry.dispose();
      }
      // Dispose material(s)
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach((mat) => disposeMaterial(mat));
        } else {
          disposeMaterial(child.material);
        }
      }
    }
  });
}

/**
 * Dispose of a material and its textures.
 */
function disposeMaterial(material: THREE.Material): void {
  // Dispose textures if present - use type guard to handle various material types
  const mat = material as unknown as Record<string, unknown>;

  // Common texture maps across material types
  const textureProps = [
    "map",
    "lightMap",
    "bumpMap",
    "normalMap",
    "envMap",
    "alphaMap",
    "aoMap",
    "displacementMap",
    "emissiveMap",
    "metalnessMap",
    "roughnessMap",
    "specularMap", // MeshPhongMaterial
    "gradientMap", // MeshToonMaterial
  ];

  for (const prop of textureProps) {
    const texture = mat[prop];
    if (texture && texture instanceof THREE.Texture) {
      texture.dispose();
    }
  }

  material.dispose();
}

/**
 * Load a 3D model based on its format.
 */
async function loadModel(
  url: string,
  format: string,
): Promise<THREE.Object3D | THREE.BufferGeometry> {
  const extension = format.toLowerCase().replace(".", "");

  switch (extension) {
    case "gltf":
    case "glb": {
      const loader = new GLTFLoader();
      const gltf = await loader.loadAsync(url);
      return gltf.scene;
    }
    case "obj": {
      const loader = new OBJLoader();
      return await loader.loadAsync(url);
    }
    case "stl": {
      const loader = new STLLoader();
      return await loader.loadAsync(url);
    }
    case "ply": {
      const loader = new PLYLoader();
      return await loader.loadAsync(url);
    }
    case "fbx": {
      const loader = new FBXLoader();
      return await loader.loadAsync(url);
    }
    default:
      throw new Error(`Unsupported format: ${format}`);
  }
}

/**
 * Center and scale an object to fit in the scene.
 */
function centerAndScaleObject(object: THREE.Object3D): void {
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());

  // Center the object
  object.position.sub(center);

  // Scale to fit in a unit sphere
  const maxDim = Math.max(size.x, size.y, size.z);
  if (maxDim > 0) {
    const scale = 2 / maxDim;
    object.scale.multiplyScalar(scale);
  }
}

/**
 * Create a mesh from a BufferGeometry (for STL, PLY formats).
 */
function createMeshFromGeometry(geometry: THREE.BufferGeometry): THREE.Mesh {
  // Compute normals if not present
  if (!geometry.attributes.normal) {
    geometry.computeVertexNormals();
  }

  // Use vertex colors if present, otherwise use default material
  const hasVertexColors = !!geometry.attributes.color;

  const material = new THREE.MeshStandardMaterial({
    color: hasVertexColors ? 0xffffff : 0x808080,
    vertexColors: hasVertexColors,
    side: THREE.DoubleSide,
    flatShading: false,
  });

  return new THREE.Mesh(geometry, material);
}

/**
 * A 3D model viewer component using Three.js.
 */
const ThreeViewer: FC<ThreeViewerProps> = ({
  url,
  format,
  height,
}): ReactElement => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const modelRef = useRef<THREE.Object3D | null>(null);
  const heightRef = useRef<number>(height);

  const [loadingState, setLoadingState] = useState<LoadingState>("loading");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [sceneReady, setSceneReady] = useState(false);

  // Keep height ref updated
  heightRef.current = height;

  // Initialize Three.js scene (only once)
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    sceneRef.current = scene;

    // Create camera
    const camera = new THREE.PerspectiveCamera(
      50,
      container.clientWidth / heightRef.current,
      0.1,
      1000,
    );
    camera.position.set(3, 2, 3);
    cameraRef.current = camera;

    // Create renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    });
    renderer.setSize(container.clientWidth, heightRef.current);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1;
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = true;
    controls.autoRotate = false;
    controlsRef.current = controls;

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight1.position.set(5, 5, 5);
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight2.position.set(-5, 3, -5);
    scene.add(directionalLight2);

    // Add a subtle ground plane grid
    const gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x333333);
    gridHelper.position.y = -1;
    scene.add(gridHelper);

    // Animation loop
    const animate = (): void => {
      animationFrameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle container width resize
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !cameraRef.current || !rendererRef.current) return;
      const width = container.clientWidth;
      cameraRef.current.aspect = width / heightRef.current;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, heightRef.current);
    });
    resizeObserver.observe(container);

    setSceneReady(true);

    // Cleanup
    return () => {
      resizeObserver.disconnect();
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      // Dispose current model before cleanup
      if (modelRef.current) {
        disposeObject(modelRef.current);
        modelRef.current = null;
      }
      if (rendererRef.current && container.contains(rendererRef.current.domElement)) {
        container.removeChild(rendererRef.current.domElement);
      }
      rendererRef.current?.dispose();
      controlsRef.current?.dispose();
      setSceneReady(false);
    };
  }, []); // Initialize only once

  // Handle height changes separately
  useEffect(() => {
    const container = containerRef.current;
    const camera = cameraRef.current;
    const renderer = rendererRef.current;

    if (!container || !camera || !renderer) return;

    const width = container.clientWidth;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }, [height]);

  // Load the 3D model
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene || !sceneReady) return;

    // Track whether this effect has been superseded
    let cancelled = false;

    setLoadingState("loading");
    setErrorMessage("");

    // Remove and dispose previous model
    if (modelRef.current) {
      scene.remove(modelRef.current);
      disposeObject(modelRef.current);
      modelRef.current = null;
    }

    // Process URL for Streamlit media paths
    const processedUrl = mergeFileUrlWithStreamlitUrl(url) || url;

    loadModel(processedUrl, format)
      .then((result) => {
        // Ignore if this load was superseded by a newer one
        if (cancelled) {
          // Dispose the loaded result since we won't use it
          if (result instanceof THREE.BufferGeometry) {
            result.dispose();
          } else if (result instanceof THREE.Object3D) {
            disposeObject(result);
          }
          return;
        }

        // Check if scene still exists (component might have unmounted)
        if (!sceneRef.current) return;

        let object: THREE.Object3D;

        if (result instanceof THREE.BufferGeometry) {
          object = createMeshFromGeometry(result);
        } else {
          object = result;
        }

        centerAndScaleObject(object);
        sceneRef.current.add(object);
        modelRef.current = object;

        // Reset camera to view the model
        if (cameraRef.current && controlsRef.current) {
          cameraRef.current.position.set(3, 2, 3);
          controlsRef.current.target.set(0, 0, 0);
          controlsRef.current.update();
        }

        setLoadingState("loaded");
      })
      .catch((error) => {
        // Ignore errors from superseded loads
        if (cancelled) return;

        console.error("Failed to load 3D model:", error);
        setLoadingState("error");
        setErrorMessage(
          error instanceof Error ? error.message : "Failed to load 3D model",
        );
      });

    // Cleanup: mark this effect as cancelled so late-resolving promises are ignored
    return () => {
      cancelled = true;
    };
  }, [url, format, sceneReady]);

  const containerStyle: CSSProperties = {
    width: "100%",
    height: `${height}px`,
    position: "relative",
    borderRadius: "8px",
    overflow: "hidden",
    backgroundColor: "#1a1a1a",
  };

  const overlayStyle: CSSProperties = {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(26, 26, 26, 0.9)",
    color: "#ffffff",
    fontFamily: "var(--st-font, sans-serif)",
    fontSize: "14px",
    zIndex: 10,
  };

  const errorStyle: CSSProperties = {
    ...overlayStyle,
    color: "#ff6b6b",
    flexDirection: "column",
    gap: "8px",
  };

  const spinnerStyle: CSSProperties = {
    width: "32px",
    height: "32px",
    border: "3px solid rgba(255, 255, 255, 0.1)",
    borderTopColor: "var(--st-primary-color, #ff4b4b)",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  };

  return (
    <>
      <style>
        {`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}
      </style>
      <div ref={containerRef} style={containerStyle}>
        {loadingState === "loading" && (
          <div style={overlayStyle}>
            <div style={spinnerStyle} />
          </div>
        )}
        {loadingState === "error" && (
          <div style={errorStyle}>
            <span>Failed to load 3D model</span>
            <span style={{ fontSize: "12px", opacity: 0.7 }}>{errorMessage}</span>
          </div>
        )}
      </div>
    </>
  );
};

export default ThreeViewer;
