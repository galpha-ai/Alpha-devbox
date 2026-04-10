import { z } from "zod";

const CHART_ARTIFACT_START = "<<<CHART_V1>>>";
const CHART_ARTIFACT_END = "<<<END_CHART_V1>>>";
const THESIS_REPORT_START = "<<<THESIS_REPORT_V1>>>";
const THESIS_REPORT_END = "<<<END_THESIS_REPORT_V1>>>";

const boundedString = (max: number) => z.string().min(1).max(max);
const boundedTime = z.string().min(1).max(40);

const chartInsightSchema = z.array(z.string().min(1).max(240)).min(1).max(8);
const chartSeriesName = boundedString(80);
const linePointSchema = z.object({
  time: boundedTime,
  value: z.number(),
});
const candlestickPointSchema = z.object({
  time: boundedTime,
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
});
const barPointSchema = z.object({
  label: boundedString(80),
  value: z.number(),
});

const lightweightLineArtifactSchema = z.object({
  schema: z.literal("chart_v1"),
  title: boundedString(160),
  summary_markdown: z.string().min(1).max(2000),
  renderer: z.literal("lightweight"),
  kind: z.enum(["line", "area"]),
  series: z.array(z.object({
    name: chartSeriesName,
    data: z.array(linePointSchema).min(1).max(240),
  })).min(1).max(4),
  insights: chartInsightSchema,
});

const lightweightCandleArtifactSchema = z.object({
  schema: z.literal("chart_v1"),
  title: boundedString(160),
  summary_markdown: z.string().min(1).max(2000),
  renderer: z.literal("lightweight"),
  kind: z.literal("candlestick"),
  series: z.array(z.object({
    name: chartSeriesName,
    data: z.array(candlestickPointSchema).min(1).max(240),
  })).min(1).max(2),
  insights: chartInsightSchema,
});

const rechartsBarArtifactSchema = z.object({
  schema: z.literal("chart_v1"),
  title: boundedString(160),
  summary_markdown: z.string().min(1).max(2000),
  renderer: z.literal("recharts"),
  kind: z.literal("bar"),
  series: z.array(z.object({
    name: chartSeriesName,
    data: z.array(barPointSchema).min(1).max(40),
  })).min(1).max(4),
  insights: chartInsightSchema,
});

export const chartArtifactV1Schema = z.union([
  lightweightLineArtifactSchema,
  lightweightCandleArtifactSchema,
  rechartsBarArtifactSchema,
]);

export type ChartArtifactV1 = z.infer<typeof chartArtifactV1Schema>;

const thesisStatSchema = z.object({
  label: boundedString(80),
  value: boundedString(80),
  sub: z.string().max(160).optional(),
});

const thesisMetricSchema = z.object({
  metric: boundedString(120),
  value: boundedString(80),
  sub: z.string().max(160).optional(),
  highlight: z.boolean(),
  positive: z.boolean().optional(),
});

const thesisPointSchema = z.object({
  x: z.number(),
  pnl: z.number(),
});

const thesisDrawdownChartSchema = z.object({
  kind: z.literal("drawdown"),
  series: z.array(z.object({
    x: z.number(),
    value: z.number(),
  })).min(1).max(120),
});

const thesisWinProbabilityChartSchema = z.object({
  kind: z.literal("winprob"),
  series: z.array(z.object({
    x: z.number(),
    primary: z.number(),
    secondary: z.number(),
  })).min(1).max(120),
});

const thesisSpreadChartSchema = z.object({
  kind: z.literal("spread"),
  series: z.array(z.object({
    label: boundedString(80),
    value: z.number(),
  })).min(1).max(40),
});

const thesisCorrelationChartSchema = z.object({
  kind: z.literal("correlation"),
  series: z.array(z.object({
    label: boundedString(80),
    value: z.number(),
    secondary: z.number(),
  })).min(1).max(40),
});

const thesisSecondaryChartSchema = z.discriminatedUnion("kind", [
  thesisDrawdownChartSchema,
  thesisWinProbabilityChartSchema,
  thesisSpreadChartSchema,
  thesisCorrelationChartSchema,
]);

const thesisMonteCarloRowSchema = z.object({
  metric: boundedString(120),
  mean: boundedString(80),
  std: boundedString(80),
  min: boundedString(80),
  max: boundedString(80),
});

const thesisSensitivityRowSchema = z.object({
  scenario: boundedString(160),
  win: boundedString(80),
  avg_pnl: boundedString(80),
  total_pnl: boundedString(80),
  tag: z.enum(["baseline", "best", "danger"]).nullable().optional(),
});

const thesisReasonSchema = z.object({
  title: boundedString(120),
  desc: z.string().min(1).max(600),
});

const thesisEconomicsRowSchema = z.object({
  label: boundedString(80),
  size: boundedString(80),
  pnl: boundedString(80),
});

export const thesisReportV1Schema = z.object({
  schema: z.literal("thesis_report_v1"),
  title: boundedString(160),
  summary_markdown: z.string().min(1).max(4000),
  stats: z.array(thesisStatSchema).min(1).max(8),
  key_metrics: z.array(thesisMetricSchema).min(1).max(16),
  pnl_series: z.array(thesisPointSchema).min(1).max(240),
  secondary_chart: thesisSecondaryChartSchema,
  monte_carlo_table: z.array(thesisMonteCarloRowSchema).min(1).max(12),
  sensitivity: z.array(thesisSensitivityRowSchema).min(1).max(12),
  reasons: z.array(thesisReasonSchema).min(1).max(8),
  economics: z.array(thesisEconomicsRowSchema).min(1).max(8),
  verdict: z.string().min(1).max(2000),
  assumptions: z.array(z.string().min(1).max(240)).max(12),
  disclaimer: z.string().min(1).max(400),
});

export type ThesisReportV1 = z.infer<typeof thesisReportV1Schema>;
export type SupportedArtifact =
  | {
      type: "chart_v1";
      data: ChartArtifactV1;
    }
  | {
      type: "thesis_report_v1";
      data: ThesisReportV1;
    };

const DEFAULT_ASSUMPTION = "Insufficient data returned by agent.";

export function extractLatestChartArtifact(text: string): ChartArtifactV1 | null {
  for (const candidate of getWrappedCandidates(text, CHART_ARTIFACT_START, CHART_ARTIFACT_END)) {
    const payload = extractJsonPayload(candidate.payload);
    if (!payload) {
      continue;
    }

    try {
      const parsed = JSON.parse(payload);
      const result = chartArtifactV1Schema.safeParse(parsed);
      if (result.success) {
        return result.data;
      }
    } catch {
      continue;
    }
  }

  return null;
}

export function extractLatestThesisReport(text: string): ThesisReportV1 | null {
  for (const candidate of getWrappedCandidates(text, THESIS_REPORT_START, THESIS_REPORT_END)) {
    const payload = extractJsonPayload(candidate.payload);
    if (!payload) {
      continue;
    }

    try {
      const parsed = JSON.parse(payload);
      const strictResult = thesisReportV1Schema.safeParse(parsed);
      if (strictResult.success) {
        return strictResult.data;
      }

      if (!shouldNormalizeReportCandidate(parsed)) {
        continue;
      }

      const normalizedResult = thesisReportV1Schema.safeParse(normalizeReportCandidate(parsed));
      if (normalizedResult.success) {
        return normalizedResult.data;
      }
    } catch {
      continue;
    }
  }

  return null;
}

export function extractLatestSupportedArtifact(text: string): SupportedArtifact | null {
  const candidates = [
    ...getWrappedCandidates(text, CHART_ARTIFACT_START, CHART_ARTIFACT_END).map((candidate) => ({
      ...candidate,
      type: "chart_v1" as const,
    })),
    ...getWrappedCandidates(text, THESIS_REPORT_START, THESIS_REPORT_END).map((candidate) => ({
      ...candidate,
      type: "thesis_report_v1" as const,
    })),
  ].sort((left, right) => right.index - left.index);

  for (const candidate of candidates) {
    if (candidate.type === "chart_v1") {
      const artifact = extractLatestChartArtifact(text.slice(candidate.index));
      if (artifact) {
        return {
          type: "chart_v1",
          data: artifact,
        };
      }
      continue;
    }

    const report = extractLatestThesisReport(text.slice(candidate.index));
    if (report) {
      return {
        type: "thesis_report_v1",
        data: report,
      };
    }
  }

  return null;
}

export function stripWrappedArtifactBlocks(content: string) {
  return content
    .replace(new RegExp(`${escapeForRegExp(CHART_ARTIFACT_START)}[\\s\\S]*?${escapeForRegExp(CHART_ARTIFACT_END)}`, "g"), "")
    .replace(new RegExp(`${escapeForRegExp(THESIS_REPORT_START)}[\\s\\S]*?${escapeForRegExp(THESIS_REPORT_END)}`, "g"), "")
    .trim();
}

function escapeForRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function getWrappedCandidates(text: string, startMarker: string, endMarker: string) {
  const matches = [...text.matchAll(new RegExp(`${escapeForRegExp(startMarker)}([\\s\\S]*?)${escapeForRegExp(endMarker)}`, "g"))];

  return matches
    .map((match) => ({
      index: match.index ?? -1,
      payload: match[1]?.trim() ?? "",
    }))
    .filter((candidate) => candidate.index >= 0)
    .sort((left, right) => right.index - left.index);
}

function extractJsonPayload(candidate: string) {
  const unfenced = candidate
    .trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/i, "")
    .trim();

  const jsonStart = unfenced.indexOf("{");
  const jsonEnd = unfenced.lastIndexOf("}");
  if (jsonStart === -1 || jsonEnd <= jsonStart) {
    return null;
  }

  return unfenced.slice(jsonStart, jsonEnd + 1);
}

function shouldNormalizeReportCandidate(candidate: unknown) {
  if (!isRecord(candidate) || candidate.schema !== "thesis_report_v1") {
    return false;
  }

  const hasArrayGap = [
    candidate.stats,
    candidate.key_metrics,
    candidate.pnl_series,
    candidate.monte_carlo_table,
    candidate.sensitivity,
    candidate.reasons,
    candidate.economics,
    candidate.assumptions,
  ].some((value) => !hasNonEmptyArray(value))
    || !("secondary_chart" in candidate);

  const secondaryChart = candidate.secondary_chart;
  if (isRecord(secondaryChart)) {
    const kind = secondaryChart.kind;
    if (typeof kind === "string" && !["drawdown", "winprob", "spread", "correlation"].includes(kind)) {
      return hasArrayGap;
    }
  }

  return hasArrayGap || hasSensitivityTagAlias(candidate.sensitivity);
}

function normalizeReportCandidate(candidate: unknown) {
  if (!isRecord(candidate)) {
    return candidate;
  }

  return {
    ...candidate,
    stats: hasNonEmptyArray(candidate.stats) ? candidate.stats : [createPlaceholderStat()],
    key_metrics: hasNonEmptyArray(candidate.key_metrics) ? candidate.key_metrics : [createPlaceholderMetric()],
    pnl_series: hasNonEmptyArray(candidate.pnl_series) ? candidate.pnl_series : createPlaceholderPnlSeries(),
    secondary_chart: normalizeSecondaryChart(candidate.secondary_chart),
    monte_carlo_table: hasNonEmptyArray(candidate.monte_carlo_table)
      ? candidate.monte_carlo_table
      : [createPlaceholderMonteCarloRow()],
    sensitivity: hasNonEmptyArray(candidate.sensitivity)
      ? normalizeSensitivityRows(candidate.sensitivity)
      : [createPlaceholderSensitivityRow()],
    reasons: hasNonEmptyArray(candidate.reasons) ? candidate.reasons : [createPlaceholderReason()],
    economics: hasNonEmptyArray(candidate.economics) ? candidate.economics : [createPlaceholderEconomicsRow()],
    assumptions: hasNonEmptyArray(candidate.assumptions) ? candidate.assumptions : [DEFAULT_ASSUMPTION],
  };
}

function normalizeSecondaryChart(value: unknown) {
  if (!isRecord(value)) {
    return createPlaceholderSecondaryChart();
  }

  const kind = value.kind;
  if (!["drawdown", "winprob", "spread", "correlation"].includes(typeof kind === "string" ? kind : "")) {
    return createPlaceholderSecondaryChart();
  }

  if (!hasNonEmptyArray(value.series)) {
    return createPlaceholderSecondaryChart();
  }

  return value;
}

function hasNonEmptyArray(value: unknown): value is unknown[] {
  return Array.isArray(value) && value.length > 0;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function createPlaceholderStat() {
  return {
    label: "Insufficient data",
    value: "N/A",
    sub: "Insufficient data",
  };
}

function createPlaceholderMetric() {
  return {
    metric: "Insufficient data",
    value: "N/A",
    sub: "Insufficient data",
    highlight: false,
    positive: false,
  };
}

function createPlaceholderPnlSeries() {
  return [
    { x: 0, pnl: 0 },
    { x: 1, pnl: 0 },
  ];
}

function createPlaceholderSecondaryChart() {
  return {
    kind: "drawdown" as const,
    series: [
      { x: 0, value: 0 },
      { x: 1, value: 0 },
    ],
  };
}

function createPlaceholderMonteCarloRow() {
  return {
    metric: "Insufficient data",
    mean: "N/A",
    std: "N/A",
    min: "N/A",
    max: "N/A",
  };
}

function normalizeSensitivityRows(rows: unknown[]) {
  return rows.map((row) => {
    if (!isRecord(row)) {
      return createPlaceholderSensitivityRow();
    }

    return {
      ...row,
      tag: normalizeSensitivityTag(row.tag),
    };
  });
}

function normalizeSensitivityTag(value: unknown) {
  if (value == null) {
    return null;
  }

  if (value === "baseline" || value === "best" || value === "danger") {
    return value;
  }

  if (value === "upside" || value === "bull") {
    return "best";
  }

  if (value === "downside" || value === "bear") {
    return "danger";
  }

  if (value === "neutral" || value === "base") {
    return "baseline";
  }

  return null;
}

function hasSensitivityTagAlias(value: unknown) {
  if (!Array.isArray(value)) {
    return false;
  }

  return value.some((row) => {
    if (!isRecord(row)) {
      return false;
    }

    return row.tag === "upside"
      || row.tag === "downside"
      || row.tag === "neutral"
      || row.tag === "bull"
      || row.tag === "bear"
      || row.tag === "base";
  });
}

function createPlaceholderSensitivityRow() {
  return {
    scenario: "Insufficient data",
    win: "N/A",
    avg_pnl: "N/A",
    total_pnl: "N/A",
    tag: "baseline" as const,
  };
}

function createPlaceholderReason() {
  return {
    title: "Insufficient data",
    desc: DEFAULT_ASSUMPTION,
  };
}

function createPlaceholderEconomicsRow() {
  return {
    label: "Insufficient data",
    size: "N/A",
    pnl: "N/A",
  };
}
