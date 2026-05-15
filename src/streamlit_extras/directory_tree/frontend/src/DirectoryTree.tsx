import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import { FC, useMemo } from "react";
import TreeNode from "./TreeNode";

export interface TreeData {
  [key: string]: TreeData | null;
}

export type DirectoryTreeStateShape = {
  selected: string;
};

export type DirectoryTreeDataShape = {
  tree: TreeData;
  expand_depth: number;
  border: boolean;
  color: string | null;
  selectable: boolean;
  height: number | null;
};

export type DirectoryTreeProps = Pick<
  FrontendRendererArgs<DirectoryTreeStateShape, DirectoryTreeDataShape>,
  "setStateValue"
> & {
  tree: TreeData;
  expandDepth: number;
  border: boolean;
  color: string | null;
  selectable: boolean;
  height: number | null;
};

const containerStyle = (
  showBorder: boolean,
  height: number | null,
): React.CSSProperties => ({
  fontFamily: "var(--st-font, sans-serif)",
  fontSize: "var(--st-base-font-size, 14px)",
  color: "var(--st-text-color, #262730)",
  padding: "8px 4px",
  overflow: "hidden",
  ...(showBorder && {
    border: "1px solid var(--st-border-color, #e6e6e9)",
    borderRadius: "var(--st-base-radius, 0.5rem)",
    padding: "12px",
  }),
  ...(height && {
    maxHeight: `${height}px`,
    overflowY: "auto" as const,
  }),
});

const DirectoryTree: FC<DirectoryTreeProps> = ({
  tree,
  expandDepth,
  border,
  color,
  selectable,
  height,
  setStateValue,
}) => {
  const style = useMemo(() => containerStyle(border, height), [border, height]);

  const handleSelect = (path: string) => {
    if (selectable) {
      setStateValue("selected", path);
    }
  };

  // Sort entries: directories first, then files, alphabetical within each group
  const sortedEntries = useMemo(() => {
    return Object.entries(tree).sort(([aName, aVal], [bName, bVal]) => {
      const aIsDir = aVal !== null;
      const bIsDir = bVal !== null;
      if (aIsDir && !bIsDir) return -1;
      if (!aIsDir && bIsDir) return 1;
      return aName.localeCompare(bName);
    });
  }, [tree]);

  return (
    <div style={style}>
      {sortedEntries.map(([name, value]) => (
        <TreeNode
          key={name}
          name={name}
          value={value}
          path={name}
          depth={0}
          expandDepth={expandDepth}
          color={color}
          selectable={selectable}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
};

export default DirectoryTree;
