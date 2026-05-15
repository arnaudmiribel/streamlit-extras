import { FC, useCallback, useEffect, useMemo, useState } from "react";
import { TreeData } from "./DirectoryTree";

type TreeNodeProps = {
  name: string;
  value: TreeData | null;
  path: string;
  depth: number;
  expandDepth: number;
  color: string | null;
  selectable: boolean;
  onSelect: (path: string) => void;
};

// Track font loading state globally (shared across all TreeNode instances)
let fontLoaded = false;
const fontLoadedListeners: Array<() => void> = [];

function notifyFontLoaded() {
  fontLoaded = true;
  for (const listener of fontLoadedListeners) {
    listener();
  }
  fontLoadedListeners.length = 0;
}

// Inject Material Symbols font and track when it's ready
const FONT_ID = "material-symbols-directory-tree";
if (typeof document !== "undefined" && !document.getElementById(FONT_ID)) {
  const link = document.createElement("link");
  link.id = FONT_ID;
  link.rel = "stylesheet";
  link.href =
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap";
  document.head.appendChild(link);

  // Wait for the font to actually load
  document.fonts.ready.then(() => {
    document.fonts
      .load("18px 'Material Symbols Outlined'")
      .then(() => notifyFontLoaded())
      .catch(() => notifyFontLoaded());
  });
} else {
  // Font link already exists, check if it's loaded
  document.fonts
    .check("18px 'Material Symbols Outlined'")
    ? (fontLoaded = true)
    : document.fonts.ready.then(() => notifyFontLoaded());
}

function useFontLoaded(): boolean {
  const [loaded, setLoaded] = useState(fontLoaded);
  useEffect(() => {
    if (fontLoaded) {
      setLoaded(true);
      return;
    }
    const listener = () => setLoaded(true);
    fontLoadedListeners.push(listener);
    return () => {
      const idx = fontLoadedListeners.indexOf(listener);
      if (idx >= 0) fontLoadedListeners.splice(idx, 1);
    };
  }, []);
  return loaded;
}

/**
 * Get a Material Symbols icon name based on file extension.
 */
function getFileIcon(filename: string): string {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  switch (ext) {
    case "py":
    case "ts":
    case "tsx":
    case "js":
    case "jsx":
    case "rs":
    case "go":
    case "java":
    case "c":
    case "cpp":
    case "h":
    case "rb":
    case "php":
    case "swift":
    case "kt":
      return "code";
    case "md":
    case "mdx":
    case "txt":
    case "rst":
      return "description";
    case "json":
    case "yaml":
    case "yml":
    case "toml":
    case "xml":
    case "ini":
    case "cfg":
    case "conf":
      return "settings";
    case "png":
    case "jpg":
    case "jpeg":
    case "gif":
    case "svg":
    case "webp":
    case "ico":
      return "image";
    case "css":
    case "scss":
    case "sass":
    case "less":
      return "palette";
    case "html":
    case "htm":
      return "web";
    case "sh":
    case "bash":
    case "zsh":
    case "fish":
      return "terminal";
    case "lock":
      return "lock";
    case "env":
      return "vpn_key";
    case "gitignore":
    case "dockerignore":
      return "visibility_off";
    default:
      return "draft";
  }
}

const iconStyle: React.CSSProperties = {
  fontFamily: "'Material Symbols Outlined'",
  fontWeight: "normal",
  fontStyle: "normal",
  fontSize: "18px",
  lineHeight: 1,
  letterSpacing: "normal",
  textTransform: "none",
  display: "inline-block",
  whiteSpace: "nowrap",
  wordWrap: "normal",
  direction: "ltr",
  fontFeatureSettings: "'liga'",
  WebkitFontSmoothing: "antialiased",
  flexShrink: 0,
  userSelect: "none",
};

const rowStyle = (
  depth: number,
  selectable: boolean,
  isHovered: boolean,
): React.CSSProperties => ({
  display: "flex",
  alignItems: "center",
  gap: "4px",
  padding: "3px 6px",
  paddingLeft: `${depth * 20 + 6}px`,
  borderRadius: "4px",
  cursor: selectable ? "pointer" : "default",
  backgroundColor: isHovered
    ? "var(--st-secondary-background-color, #f0f2f6)"
    : "transparent",
  transition: "background-color 0.1s ease",
  userSelect: "none",
  minWidth: 0,
  overflow: "hidden",
});

const nameStyle: React.CSSProperties = {
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
  lineHeight: "24px",
  minWidth: 0,
};

const TreeNode: FC<TreeNodeProps> = ({
  name,
  value,
  path,
  depth,
  expandDepth,
  color,
  selectable,
  onSelect,
}) => {
  const isDirectory = value !== null;
  const [isExpanded, setIsExpanded] = useState(depth < expandDepth);
  const [isHovered, setIsHovered] = useState(false);
  const isFontReady = useFontLoaded();

  const handleClick = useCallback(() => {
    if (isDirectory) {
      setIsExpanded((prev) => !prev);
    }
    if (selectable) {
      onSelect(path);
    }
  }, [isDirectory, selectable, onSelect, path]);

  const icon = useMemo(() => {
    if (isDirectory) {
      return isExpanded ? "folder_open" : "folder";
    }
    return getFileIcon(name);
  }, [isDirectory, isExpanded, name]);

  const iconColor = useMemo((): string => {
    if (isDirectory) {
      if (color === null) {
        return "var(--st-text-color, #262730)";
      }
      if (color === "primary") {
        return "var(--st-primary-color, #ff4b4b)";
      }
      return color;
    }
    return "var(--st-text-color, #262730)";
  }, [isDirectory, color]);

  // Sort children: directories first, then files
  const sortedChildren = useMemo(() => {
    if (!isDirectory || value === null) return [];
    return Object.entries(value).sort(([aName, aVal], [bName, bVal]) => {
      const aIsDir = aVal !== null;
      const bIsDir = bVal !== null;
      if (aIsDir && !bIsDir) return -1;
      if (!aIsDir && bIsDir) return 1;
      return aName.localeCompare(bName);
    });
  }, [isDirectory, value]);

  return (
    <div>
      <div
        style={rowStyle(depth, selectable || isDirectory, isHovered)}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        role={selectable ? "button" : undefined}
        tabIndex={selectable || isDirectory ? 0 : undefined}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            handleClick();
          }
        }}
      >
        {/* Chevron for directories — always use SVG so there's no FOUT */}
        {isDirectory ? (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              width: "16px",
              height: "16px",
              flexShrink: 0,
              transition: "transform 0.15s ease",
              transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)",
              opacity: 0.6,
            }}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M6 4L10 8L6 12"
                stroke="var(--st-text-color, #262730)"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
        ) : (
          <span style={{ width: "16px", flexShrink: 0 }} />
        )}

        {/* File/folder icon — hidden until font loads to avoid FOUT */}
        <span
          style={{
            ...iconStyle,
            color: iconColor,
            visibility: isFontReady ? "visible" : "hidden",
          }}
        >
          {icon}
        </span>

        {/* Name */}
        <span style={nameStyle}>{name}</span>
      </div>

      {/* Children (only render when expanded) */}
      {isDirectory && isExpanded && (
        <div>
          {sortedChildren.map(([childName, childValue]) => (
            <TreeNode
              key={childName}
              name={childName}
              value={childValue}
              path={`${path}/${childName}`}
              depth={depth + 1}
              expandDepth={expandDepth}
              color={color}
              selectable={selectable}
              onSelect={onSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;
