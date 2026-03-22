import { FrontendRendererArgs } from "@streamlit/component-v2-lib";
import React, { useState, useRef, useEffect } from "react";

// Types
export type ColumnType = "text" | "number" | "date" | "boolean" | "option";

export interface ColumnConfig {
  id: string;
  name: string;
  type: ColumnType;
  options: string[] | null;
}

export interface FilterCondition {
  column: string;
  operator: string;
  value: string | string[] | [string, string];
}

export interface DataframeFilterDataShape {
  columns: ColumnConfig[];
}

export interface DataframeFilterStateShape {
  filters: FilterCondition[];
  [key: string]: unknown;
}

// Operator definitions per column type
const OPERATORS: Record<ColumnType, { value: string; label: string }[]> = {
  text: [
    { value: "contains", label: "contains" },
    { value: "not_contains", label: "does not contain" },
    { value: "equals", label: "equals" },
    { value: "not_equals", label: "does not equal" },
    { value: "starts_with", label: "starts with" },
    { value: "ends_with", label: "ends with" },
    { value: "is_empty", label: "is empty" },
    { value: "is_not_empty", label: "is not empty" },
  ],
  number: [
    { value: "equals", label: "=" },
    { value: "not_equals", label: "≠" },
    { value: "greater_than", label: ">" },
    { value: "greater_than_or_equal", label: "≥" },
    { value: "less_than", label: "<" },
    { value: "less_than_or_equal", label: "≤" },
    { value: "between", label: "between" },
    { value: "is_empty", label: "is empty" },
    { value: "is_not_empty", label: "is not empty" },
  ],
  date: [
    { value: "equals", label: "is" },
    { value: "before", label: "before" },
    { value: "after", label: "after" },
    { value: "between", label: "between" },
    { value: "is_empty", label: "is empty" },
    { value: "is_not_empty", label: "is not empty" },
  ],
  boolean: [
    { value: "is_true", label: "is true" },
    { value: "is_false", label: "is false" },
    { value: "is_empty", label: "is empty" },
  ],
  option: [
    { value: "equals", label: "is" },
    { value: "not_equals", label: "is not" },
    { value: "is_any_of", label: "is any of" },
    { value: "is_none_of", label: "is none of" },
    { value: "is_empty", label: "is empty" },
    { value: "is_not_empty", label: "is not empty" },
  ],
};

const requiresValue = (operator: string): boolean => {
  return !["is_empty", "is_not_empty", "is_true", "is_false"].includes(operator);
};

const requiresTwoValues = (operator: string): boolean => {
  return operator === "between";
};

const allowsMultipleValues = (operator: string): boolean => {
  return ["is_any_of", "is_none_of"].includes(operator);
};

interface FilterRowProps {
  filter: FilterCondition;
  index: number;
  columns: ColumnConfig[];
  onUpdate: (index: number, filter: FilterCondition) => void;
  onRemove: (index: number) => void;
}

const FilterRow: React.FC<FilterRowProps> = ({
  filter,
  index,
  columns,
  onUpdate,
  onRemove,
}) => {
  const column = columns.find((c) => c.id === filter.column);
  const columnType = column?.type || "text";
  const operators = OPERATORS[columnType];
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleColumnChange = (newColumn: string) => {
    const newCol = columns.find((c) => c.id === newColumn);
    const newType = newCol?.type || "text";
    const defaultOp = OPERATORS[newType][0].value;
    onUpdate(index, {
      column: newColumn,
      operator: defaultOp,
      value: allowsMultipleValues(defaultOp) ? [] : "",
    });
  };

  const handleOperatorChange = (newOperator: string) => {
    const newValue = allowsMultipleValues(newOperator)
      ? []
      : requiresTwoValues(newOperator)
        ? ["", ""]
        : "";
    onUpdate(index, { ...filter, operator: newOperator, value: newValue });
  };

  const handleValueChange = (newValue: string | string[]) => {
    onUpdate(index, { ...filter, value: newValue });
  };

  const handleBetweenValueChange = (idx: 0 | 1, val: string) => {
    const currentValue = Array.isArray(filter.value) ? filter.value : ["", ""];
    const newValue = [...currentValue] as [string, string];
    newValue[idx] = val;
    onUpdate(index, { ...filter, value: newValue });
  };

  const handleMultiSelectToggle = (option: string) => {
    const currentValues = Array.isArray(filter.value) ? (filter.value as string[]) : [];
    const newValues = currentValues.includes(option)
      ? currentValues.filter((v) => v !== option)
      : [...currentValues, option];
    handleValueChange(newValues);
  };

  const renderValueInput = () => {
    if (!requiresValue(filter.operator)) {
      return null;
    }

    if (requiresTwoValues(filter.operator)) {
      const values = Array.isArray(filter.value) ? filter.value : ["", ""];
      return (
        <div className="filter-between">
          <input
            type={columnType === "date" ? "date" : "text"}
            value={values[0] || ""}
            onChange={(e) => handleBetweenValueChange(0, e.target.value)}
            placeholder={columnType === "date" ? "" : "min"}
            className="filter-input filter-input-small"
          />
          <span className="filter-between-separator">–</span>
          <input
            type={columnType === "date" ? "date" : "text"}
            value={values[1] || ""}
            onChange={(e) => handleBetweenValueChange(1, e.target.value)}
            placeholder={columnType === "date" ? "" : "max"}
            className="filter-input filter-input-small"
          />
        </div>
      );
    }

    if (allowsMultipleValues(filter.operator) && column?.options) {
      const selectedValues = Array.isArray(filter.value) ? (filter.value as string[]) : [];
      return (
        <div className="filter-multiselect" ref={dropdownRef}>
          <button
            type="button"
            className="filter-multiselect-trigger"
            onClick={() => setIsOpen(!isOpen)}
          >
            {selectedValues.length === 0 ? "Select..." : `${selectedValues.length} selected`}
            <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
              <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          {isOpen && (
            <div className="filter-multiselect-dropdown">
              {column.options.map((option) => (
                <label key={option} className="filter-multiselect-option">
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option)}
                    onChange={() => handleMultiSelectToggle(option)}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (columnType === "option" && column?.options) {
      return (
        <select
          value={filter.value as string}
          onChange={(e) => handleValueChange(e.target.value)}
          className="filter-select"
        >
          <option value="">Select...</option>
          {column.options.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      );
    }

    return (
      <input
        type={columnType === "number" ? "number" : columnType === "date" ? "date" : "text"}
        value={filter.value as string}
        onChange={(e) => handleValueChange(e.target.value)}
        placeholder="value"
        className="filter-input"
      />
    );
  };

  return (
    <div className="filter-chip">
      <div className="filter-chip-content">
        <select
          value={filter.column}
          onChange={(e) => handleColumnChange(e.target.value)}
          className="filter-select filter-select-column"
        >
          {columns.map((col) => (
            <option key={col.id} value={col.id}>{col.name}</option>
          ))}
        </select>
        <select
          value={filter.operator}
          onChange={(e) => handleOperatorChange(e.target.value)}
          className="filter-select"
        >
          {operators.map((op) => (
            <option key={op.value} value={op.value}>{op.label}</option>
          ))}
        </select>
        {renderValueInput()}
      </div>
      <button
        type="button"
        onClick={() => onRemove(index)}
        className="filter-remove-btn"
        aria-label="Remove filter"
      >
        <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
          <path d="M10.5 3.5L3.5 10.5M3.5 3.5L10.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </div>
  );
};

export type DataframeFilterProps = Pick<
  FrontendRendererArgs<DataframeFilterStateShape, DataframeFilterDataShape>,
  "setStateValue"
> & {
  columns: ColumnConfig[];
  initialFilters?: FilterCondition[];
};

const DataframeFilter: React.FC<DataframeFilterProps> = ({
  columns,
  setStateValue,
  initialFilters = [],
}) => {
  const [filters, setFilters] = useState<FilterCondition[]>(initialFilters);

  const updateFilters = (newFilters: FilterCondition[]) => {
    setFilters(newFilters);
    setStateValue("filters", newFilters);
  };

  const addFilter = () => {
    if (columns.length === 0) return;
    const defaultColumn = columns[0];
    const defaultOperator = OPERATORS[defaultColumn.type][0].value;
    const newFilter: FilterCondition = {
      column: defaultColumn.id,
      operator: defaultOperator,
      value: allowsMultipleValues(defaultOperator) ? [] : "",
    };
    updateFilters([...filters, newFilter]);
  };

  const updateFilter = (index: number, filter: FilterCondition) => {
    const newFilters = [...filters];
    newFilters[index] = filter;
    updateFilters(newFilters);
  };

  const removeFilter = (index: number) => {
    const newFilters = filters.filter((_, i) => i !== index);
    updateFilters(newFilters);
  };

  const clearAllFilters = () => {
    updateFilters([]);
  };

  return (
    <div className="filter-container">
      <div className="filter-bar">
        {filters.map((filter, index) => (
          <FilterRow
            key={index}
            filter={filter}
            index={index}
            columns={columns}
            onUpdate={updateFilter}
            onRemove={removeFilter}
          />
        ))}

        <button type="button" onClick={addFilter} className="filter-add-btn" aria-label="Add filter">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 2.5V11.5M2.5 7H11.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>

        {filters.length > 0 && (
          <button type="button" onClick={clearAllFilters} className="filter-clear-btn">
            Clear all
          </button>
        )}
      </div>
    </div>
  );
};

export default DataframeFilter;
