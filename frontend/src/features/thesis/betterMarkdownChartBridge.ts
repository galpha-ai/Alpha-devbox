import type {
  ChartRecommendation as CoreChartRecommendation,
  ColumnMeta,
  DataTable,
} from "./betterMarkdownChartCore";

export type ThesisChartType =
  | "bar"
  | "horizontal-bar"
  | "line"
  | "area"
  | "radar"
  | "scatter"
  | "composed";

export type UpstreamChartType = string;

const UPSTREAM_CHART_TYPES = new Set<UpstreamChartType>([
  "bar",
  "horizontal-bar",
  "stacked-bar",
  "line",
  "area",
  "radar",
  "pie",
  "donut",
  "composed",
  "scatter",
  "heatmap",
  "candlestick",
  "ohlc",
  "tv-line",
  "tv-area",
  "baseline",
  "tv-histogram",
  "waterfall",
  "histogram",
  "drawdown",
  "volume-profile",
  "cumulative-return",
  "equity-curve",
  "loss-curve",
  "pred-vs-actual",
  "residual",
  "compare",
  "metric-summary",
  "distribution",
  "timeline",
  "bubble",
  "funnel",
  "treemap",
]);

const THESIS_CHART_TYPES: ThesisChartType[] = [
  "bar",
  "horizontal-bar",
  "line",
  "area",
  "radar",
  "scatter",
  "composed",
];

const TABLE_FALLBACK_TYPES = new Set<UpstreamChartType>([
  "candlestick",
  "ohlc",
  "tv-histogram",
  "volume-profile",
]);

export interface DirectiveResolutionContext {
  hasNegativeValues: boolean;
}

export interface DirectiveResolution {
  type: ThesisChartType;
  valueColumnsMode: "keep" | "clear";
  reason: string;
}

export interface ChartTypeResolutionContext {
  hasNegativeValues: boolean;
  source: "directive" | "recommendation";
}

export interface ThesisAdaptedRecommendation extends Omit<CoreChartRecommendation, "type" | "alternatives"> {
  type: ThesisChartType;
  alternatives: ThesisChartType[];
}

function resolveUpstreamChartType(
  upstreamType: UpstreamChartType,
  context: ChartTypeResolutionContext,
): DirectiveResolution {
  const sourcePrefix = context.source === "directive" ? "Directive" : "Recommendation";

  if (THESIS_CHART_TYPES.includes(upstreamType as ThesisChartType)) {
    return {
      type: upstreamType as ThesisChartType,
      valueColumnsMode: "keep",
      reason: context.source === "directive" ? "Directive override" : "Recommendation preserved",
    };
  }

  if (TABLE_FALLBACK_TYPES.has(upstreamType)) {
    return {
      type: "bar",
      valueColumnsMode: "clear",
      reason: `${sourcePrefix} fallback from unsupported specialist type: ${upstreamType}`,
    };
  }

  if (upstreamType === "tv-area" || upstreamType === "drawdown") {
    return {
      type: "area",
      valueColumnsMode: "keep",
      reason: `${sourcePrefix} downgrade from ${upstreamType} to thesis-safe area`,
    };
  }

  if (upstreamType === "bubble") {
    return {
      type: "scatter",
      valueColumnsMode: "keep",
      reason: `${sourcePrefix} downgrade from bubble to thesis-safe scatter`,
    };
  }

  if (
    upstreamType === "tv-line"
    || upstreamType === "baseline"
    || upstreamType === "cumulative-return"
    || upstreamType === "equity-curve"
    || upstreamType === "loss-curve"
    || upstreamType === "pred-vs-actual"
    || upstreamType === "residual"
    || upstreamType === "timeline"
  ) {
    return {
      type: "line",
      valueColumnsMode: "keep",
      reason: `${sourcePrefix} downgrade from ${upstreamType} to thesis-safe line`,
    };
  }

  if (
    upstreamType === "stacked-bar"
    || upstreamType === "compare"
    || upstreamType === "metric-summary"
    || upstreamType === "histogram"
    || upstreamType === "distribution"
    || upstreamType === "funnel"
    || upstreamType === "treemap"
    || upstreamType === "pie"
    || upstreamType === "donut"
  ) {
    return {
      type: "bar",
      valueColumnsMode: "keep",
      reason: `${sourcePrefix} downgrade from ${upstreamType} to thesis-safe bar`,
    };
  }

  if (upstreamType === "waterfall" || upstreamType === "heatmap") {
    return {
      type: "composed",
      valueColumnsMode: "keep",
      reason: `${sourcePrefix} downgrade from ${upstreamType} to thesis-safe composed`,
    };
  }

  return {
    type: context.hasNegativeValues ? "line" : "area",
    valueColumnsMode: "keep",
    reason: `${sourcePrefix} downgrade from ${upstreamType} using thesis time-series fallback`,
  };
}

export function adaptRecommendationForThesis(
  recommendation: CoreChartRecommendation,
  columns: ColumnMeta[],
  table: DataTable,
  contextTitle?: string,
): ThesisAdaptedRecommendation {
  const hasNegativeValues = columns.some((column) => column.stats?.hasNegative);
  const hasDateColumn = columns.some((column) => column.type === "date");
  const multiMetricComparison = recommendation.valueColumns.length >= 3 && table.rows.length >= 2 && table.rows.length <= 8;

  const thesisAdjustedRecommendation: CoreChartRecommendation =
    !table.directive?.type && !hasDateColumn && multiMetricComparison
      ? {
        ...recommendation,
        type: "radar",
        alternatives: ["bar", "composed", "line", ...recommendation.alternatives],
        normalize: needsRadarNormalization(columns, recommendation.valueColumns),
      }
      : recommendation;

  const resolvedType = resolveUpstreamChartType(thesisAdjustedRecommendation.type, {
    hasNegativeValues,
    source: table.directive?.type ? "directive" : "recommendation",
  });

  return {
    ...thesisAdjustedRecommendation,
    type: resolvedType.type,
    alternatives: normalizeAlternatives(thesisAdjustedRecommendation, hasNegativeValues, resolvedType.type),
    valueColumns: resolvedType.valueColumnsMode === "clear"
      ? []
      : [...thesisAdjustedRecommendation.valueColumns],
    reason: resolvedType.reason === "Recommendation preserved"
      ? thesisAdjustedRecommendation.reason
      : resolvedType.reason,
    suggestedTitle: table.directive?.title ?? thesisAdjustedRecommendation.suggestedTitle ?? contextTitle,
  };
}

function normalizeAlternatives(
  recommendation: CoreChartRecommendation,
  hasNegativeValues: boolean,
  chosenType: ThesisChartType,
): ThesisChartType[] {
  const mapped = recommendation.alternatives
    .map((alternative) => resolveUpstreamChartType(alternative, {
      hasNegativeValues,
      source: "recommendation",
    }))
    .filter((resolution) => resolution.valueColumnsMode === "keep")
    .map((resolution) => resolution.type)
    .filter((type) => type !== chosenType);

  const unique = new Set<ThesisChartType>();
  for (const type of mapped) {
    unique.add(type);
  }

  for (const fallback of THESIS_CHART_TYPES) {
    if (fallback !== chosenType) {
      unique.add(fallback);
    }
    if (unique.size >= 4) {
      break;
    }
  }

  return [...unique];
}

function needsRadarNormalization(columns: ColumnMeta[], valueColumns: string[]) {
  const positiveRanges = columns
    .filter((column) => valueColumns.includes(column.name))
    .map((column) => column.stats?.range ?? 0)
    .filter((range) => range > 0);

  if (positiveRanges.length < 2) {
    return false;
  }

  return Math.max(...positiveRanges) / Math.min(...positiveRanges) > 10;
}
