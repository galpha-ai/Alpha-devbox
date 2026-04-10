import type {
  AxisConfig,
  ChartReadyData as CoreChartReadyData,
  ChartRecommendation as CoreChartRecommendation,
  ChartDirective as CoreChartDirective,
  ColumnCorrelation,
  ColumnMeta,
  ColumnStats,
  ColumnType,
  DataTable as CoreDataTable,
  NumericFormat,
} from "./betterMarkdownChartCore";
import {
  extractTables,
  normalizeRecords,
  processTable as coreProcessTable,
} from "./betterMarkdownChartCore";
import {
  adaptRecommendationForThesis,
  type ThesisChartType,
} from "./betterMarkdownChartBridge";

export type MdChartType = ThesisChartType;
export type ChartDirective = CoreChartDirective;
export type DataTable = CoreDataTable;
export type { AxisConfig, ColumnCorrelation, ColumnMeta, ColumnStats, ColumnType, NumericFormat };

export interface ChartRecommendation extends Omit<CoreChartRecommendation, "type" | "alternatives"> {
  type: MdChartType;
  alternatives: MdChartType[];
}

export interface ChartReadyData extends Omit<CoreChartReadyData, "recommendation"> {
  recommendation: ChartRecommendation;
}

export interface MarkdownSegment {
  type: "text" | "table";
  content: string;
  chartData?: ChartReadyData;
}

export { analyzeColumns, computeCorrelations, formatValue, parseNumeric } from "./betterMarkdownChartCore";

export function segmentMarkdown(markdown: string): MarkdownSegment[] {
  const tables = extractTables(markdown);
  if (tables.length === 0) {
    return [{ type: "text", content: markdown }];
  }

  const segments: MarkdownSegment[] = [];
  let cursor = 0;

  for (const table of tables) {
    const rawProse = markdown.slice(cursor, table.startIndex);
    const { content: prose, title: contextTitle } = splitProseContext(rawProse);
    if (prose) {
      segments.push({ type: "text", content: prose });
    }

    segments.push({
      type: "table",
      content: table.rawMarkdown,
      chartData: processTable(table, contextTitle),
    });

    cursor = table.endIndex;
  }

  const remaining = markdown.slice(cursor).trim();
  if (remaining) {
    segments.push({ type: "text", content: remaining });
  }

  return segments;
}

export function processTable(table: DataTable, contextTitle?: string): ChartReadyData {
  const coreChartData = coreProcessTable(table);
  const recommendation = adaptRecommendationForThesis(
    coreChartData.recommendation,
    coreChartData.columns,
    table,
    contextTitle,
  );

  const records = coreChartData.records;
  const normalizedRecords = recommendation.normalize
    ? (coreChartData.normalizedRecords ?? normalizeRecords(records, recommendation.valueColumns))
    : undefined;

  return {
    ...coreChartData,
    recommendation,
    records,
    normalizedRecords,
  };
}

function splitProseContext(prose: string) {
  const trimmed = prose.trim();
  if (!trimmed) {
    return {
      content: "",
      title: undefined,
    };
  }

  const lines = trimmed.split("\n");
  let scanIndex = lines.length - 1;
  while (scanIndex >= 0 && !lines[scanIndex]?.trim()) {
    scanIndex -= 1;
  }

  while (scanIndex >= 0 && isChartDirectiveLine(lines[scanIndex]?.trim() ?? "")) {
    scanIndex -= 1;
  }

  if (scanIndex < 0) {
    return {
      content: "",
      title: undefined,
    };
  }

  const trailingTitle = parseSectionLabel(lines[scanIndex]?.trim() ?? "");
  if (trailingTitle) {
    return {
      content: lines.slice(0, scanIndex).join("\n").trim(),
      title: trailingTitle,
    };
  }

  const normalizedContent = lines.slice(0, scanIndex + 1).join("\n").trim();

  return {
    content: normalizedContent,
    title: inferContextTitle(normalizedContent),
  };
}

function inferContextTitle(prose: string) {
  const lines = prose
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const title = parseSectionLabel(lines[index] ?? "");
    if (title) {
      return title;
    }
  }

  return undefined;
}

function parseSectionLabel(line: string) {
  if (!line) {
    return undefined;
  }

  const heading = line.match(/^#{1,6}\s+(.+)$/);
  if (heading?.[1]) {
    return cleanSectionLabel(heading[1]);
  }

  const emphasized = line.match(/^(?:\*\*|__)(.+?)(?:\*\*|__)[:]??\s*$/);
  if (emphasized?.[1]) {
    return cleanSectionLabel(emphasized[1]);
  }

  if (line.endsWith(":") && line.length <= 80 && !/[.!?]:$/.test(line)) {
    return cleanSectionLabel(line.slice(0, -1));
  }

  if (line.length <= 48 && !/[.!?]$/.test(line)) {
    return cleanSectionLabel(line);
  }

  return undefined;
}

function cleanSectionLabel(line: string) {
  const cleaned = line
    .replace(/[`*_]/g, "")
    .replace(/\s+/g, " ")
    .trim();

  return cleaned || undefined;
}

function isChartDirectiveLine(line: string) {
  return /^<!--\s*chart:?/i.test(line);
}
