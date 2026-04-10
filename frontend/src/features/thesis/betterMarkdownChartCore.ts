/**
 * better-markdown chart pipeline — production-grade middleware
 *
 * Layer 1: Parser     — MD string → DataTable[] (robust, position-preserving)
 * Layer 2: Analyzer   — DataTable → ColumnMeta[] (type inference, rich statistics)
 * Layer 3: Advisor    — DataTable + ColumnMeta → ChartRecommendation (pluggable)
 * Layer 4: Renderer   — ChartRecommendation + data → React component (swappable)
 *
 * Design principles:
 *  - Zero dependencies in parser/analyzer/advisor (pure functions)
 *  - Every layer is independently usable
 *  - Graceful degradation on malformed input
 *  - Rich metadata for downstream consumers
 */

// ═══════════════════════════════════════════════════════════════════
//  TYPES
// ═══════════════════════════════════════════════════════════════════

export interface DataTable {
  headers: string[];
  rows: string[][];
  /** Raw markdown source for this table */
  rawMarkdown: string;
  /** Byte position in the original markdown string */
  startIndex: number;
  endIndex: number;
  /** Column alignment hints from separator row (left|center|right|none) */
  alignments: ('left' | 'center' | 'right' | 'none')[];
  /** Optional directive hint parsed from <!-- chart:type --> comment */
  directive?: ChartDirective;
}

export interface ChartDirective {
  type?: ChartType;
  title?: string;
  height?: number;
  /** Any extra key=value pairs from the directive */
  options: Record<string, string>;
}

export type ColumnType = 'number' | 'percentage' | 'currency' | 'date' | 'ordinal' | 'string';

export interface NumericFormat {
  prefix: string;     // '$', '€', etc.
  suffix: string;     // '%', 'ms', etc.
  decimals: number;   // max decimal places seen
  isCompact: boolean; // uses K/M/B notation
}

export interface ColumnStats {
  min: number;
  max: number;
  mean: number;
  median: number;
  sum: number;
  stdDev: number;
  hasNegative: boolean;
  /** Number of distinct values */
  cardinality: number;
  /** Indices of statistical outliers (>2 stdDev from mean) */
  outlierIndices: number[];
  /** Quartiles [Q1, Q2/median, Q3] */
  quartiles: [number, number, number];
  /** Range (max - min) */
  range: number;
}

export interface ColumnMeta {
  name: string;
  index: number;
  type: ColumnType;
  /** Ratio of non-null parseable values (0-1) */
  confidence: number;
  stats?: ColumnStats;
  /** Detected number format for tooltip/label formatting */
  format?: NumericFormat;
  /** Number of null/unparseable values */
  nullCount: number;
}

/**
 * ChartType is an extensible string — not a fixed union.
 * Built-in types are listed here; adapters can support any additional types.
 */
export type ChartType = string;

/** Well-known built-in chart types */
export type BuiltinChartType =
  | 'bar' | 'horizontal-bar' | 'stacked-bar' | 'line' | 'area'
  | 'radar' | 'pie' | 'donut' | 'composed' | 'scatter' | 'heatmap'
  // Quant / Finance
  | 'candlestick' | 'ohlc' | 'tv-line' | 'tv-area' | 'baseline' | 'tv-histogram'
  | 'waterfall' | 'histogram' | 'drawdown' | 'volume-profile'
  | 'cumulative-return' | 'equity-curve'
  // Data Science / ML
  | 'boxplot' | 'violin' | 'bubble' | 'treemap' | 'sunburst'
  | 'funnel' | 'gauge' | 'sankey' | 'parallel-coordinates'
  | 'residual' | 'pred-vs-actual' | 'loss-curve'
  // Distribution / Stats
  | 'distribution' | 'qq-plot' | 'density-curve'
  // Research / Experiment
  | 'timeline' | 'compare' | 'metric-summary';

export interface AxisConfig {
  column: string;
  position: 'left' | 'right' | 'bottom';
  label?: string;
  /** Suggested domain override [min, max] */
  domain?: [number | 'auto', number | 'auto'];
}

export interface ChartRecommendation {
  type: ChartType;
  /** 0-1, how confident the advisor is */
  confidence: number;
  labelColumn: string;
  valueColumns: string[];
  reason: string;
  /** Alternative chart types that could also work */
  alternatives: ChartType[];
  /** Sorting suggestion */
  sortBy?: { column: string; direction: 'asc' | 'desc' };
  /** Whether data should be normalized (e.g. for radar with different scales) */
  normalize?: boolean;
  /** Axis configuration hints */
  axes?: AxisConfig[];
  /** Suggested title inferred from data */
  suggestedTitle?: string;
}

export interface ChartReadyData {
  table: DataTable;
  columns: ColumnMeta[];
  recommendation: ChartRecommendation;
  /** Parsed numeric data ready for charting */
  records: Record<string, string | number>[];
  /** Normalized records (0-1 scale) for radar charts */
  normalizedRecords?: Record<string, string | number>[];
  /** Column correlations (Pearson r) for scatter detection */
  correlations?: ColumnCorrelation[];
}

export interface ColumnCorrelation {
  column1: string;
  column2: string;
  r: number; // Pearson correlation coefficient
}

// ═══════════════════════════════════════════════════════════════════
//  LAYER 1: PARSER
// ═══════════════════════════════════════════════════════════════════

/** Parse a value string into a numeric result with detected type */
export function parseNumeric(val: string): { value: number; type: ColumnType; format: NumericFormat } | null {
  const trimmed = val.trim();
  if (!trimmed || trimmed === '-' || /^(N\/A|n\/a|null|none|—|–)$/i.test(trimmed)) return null;

  // Detect format markers before stripping
  const isCurrency = /^[$€¥£₹₿]|USD|EUR|GBP|JPY/.test(trimmed) || /\$\s*$/.test(trimmed);
  const isPercentage = /%\s*$/.test(trimmed);
  const prefix = (trimmed.match(/^([$€¥£₹₿])\s*/)?.[1]) || '';
  const suffix = isPercentage ? '%' : '';

  // Handle parenthetical negatives: ($1,234) or (1,234)
  let cleaned = trimmed;
  let negative = false;
  if (/^\(.*\)$/.test(cleaned)) {
    cleaned = cleaned.slice(1, -1);
    negative = true;
  }

  // Handle compact notation: 1.2K, 3.5M, 2B
  let compactMultiplier = 1;
  let isCompact = false;
  const compactMatch = cleaned.match(/([0-9.]+)\s*([KkMmBbTt])\s*$/);
  if (compactMatch) {
    const units: Record<string, number> = { k: 1e3, m: 1e6, b: 1e9, t: 1e12 };
    compactMultiplier = units[compactMatch[2].toLowerCase()] || 1;
    cleaned = compactMatch[1];
    isCompact = true;
  }

  cleaned = cleaned.replace(/[$%,+€¥£₹₿\s]/g, '').trim();

  // Handle leading negative sign
  if (cleaned.startsWith('-')) {
    negative = true;
    cleaned = cleaned.slice(1);
  }

  const num = parseFloat(cleaned);
  if (isNaN(num) || !isFinite(num)) return null;

  const value = (negative ? -num : num) * compactMultiplier;
  const decimals = cleaned.includes('.') ? (cleaned.split('.')[1]?.length || 0) : 0;
  const type: ColumnType = isCurrency ? 'currency' : isPercentage ? 'percentage' : 'number';

  return { value, type, format: { prefix, suffix, decimals, isCompact } };
}

/** Detect if a string looks like a date/time value */
function isDateLike(val: string): boolean {
  const v = val.trim();
  const patterns = [
    /^\d{4}[-/]\d{1,2}([-/]\d{1,2})?$/,
    /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s*\d{0,4}/i,
    /^Q[1-4]\s*['']?\d{2,4}$/i,
    /^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$/,
    /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\w*/i,
    /^Week\s*\d+/i,
    /^(FY|H[12]|CY)\s*\d{2,4}/i,
    /^(19|20)\d{2}$/,  // Just a year (1900-2099 only)
    /^(Spring|Summer|Fall|Autumn|Winter)\s*\d{0,4}/i,
  ];
  return patterns.some(p => p.test(v));
}

/** Detect ordinal strings (1st, 2nd, Rank 1, etc.) */
function isOrdinal(val: string): boolean {
  return /^(#\d+|Rank\s*\d+|\d+(st|nd|rd|th))$/i.test(val.trim());
}

/** Parse column alignment from GFM separator row */
function parseAlignments(separator: string): ('left' | 'center' | 'right' | 'none')[] {
  return separator.split('|').slice(1, -1).map(cell => {
    const c = cell.trim();
    const left = c.startsWith(':');
    const right = c.endsWith(':');
    if (left && right) return 'center';
    if (right) return 'right';
    if (left) return 'left';
    return 'none';
  });
}

/** Parse a chart directive from an HTML comment: <!-- chart:tv-line title="..." height=400 --> */
function parseDirective(comment: string): ChartDirective | undefined {
  const match = comment.match(/<!--\s*chart:?([\w-]+)?\s*(.*?)\s*-->/i);
  if (!match) return undefined;

  const type = match[1] as ChartType | undefined;
  const rest = match[2] || '';
  const options: Record<string, string> = {};

  // Parse key=value and key="value with spaces"
  const kvRegex = /(\w+)=(?:"([^"]*)"|([\S]+))/g;
  let kv;
  while ((kv = kvRegex.exec(rest)) !== null) {
    options[kv[1]] = kv[2] ?? kv[3];
  }

  return {
    type: type && isValidChartType(type) ? type : undefined,
    title: options.title,
    height: options.height ? parseInt(options.height) : undefined,
    options,
  };
}

function isValidChartType(t: string): t is ChartType {
  return ['bar', 'horizontal-bar', 'stacked-bar', 'line', 'area', 'radar', 'pie', 'donut', 'composed', 'scatter', 'heatmap',
    'candlestick', 'ohlc', 'tv-line', 'tv-area', 'baseline', 'tv-histogram', 'waterfall', 'histogram', 'drawdown', 'volume-profile',
    'cumulative-return', 'equity-curve', 'loss-curve', 'pred-vs-actual', 'residual', 'compare', 'metric-summary',
    'distribution', 'timeline', 'bubble', 'funnel', 'treemap'].includes(t);
}

function splitRow(line: string): string[] {
  return line.split('|').slice(1, -1).map(c => c.trim());
}

/** Extract all tables from markdown, preserving positions and parsing directives */
export function extractTables(md: string): DataTable[] {
  const tables: DataTable[] = [];
  const lines = md.split('\n');
  let i = 0;
  let charPos = 0;
  let lastDirective: ChartDirective | undefined;

  while (i < lines.length) {
    const lineStart = charPos;
    const line = lines[i].trim();

    // Check for chart directive comment
    const directive = parseDirective(line);
    if (directive) {
      lastDirective = directive;
      charPos += lines[i].length + 1;
      i++;
      continue;
    }

    if (line.startsWith('|') && line.endsWith('|')) {
      if (i + 1 < lines.length && /^\|[\s\-:|]+\|$/.test(lines[i + 1].trim())) {
        const headers = splitRow(line);
        const alignments = parseAlignments(lines[i + 1].trim());
        const startIndex = lineStart;
        i += 2;
        charPos += lines[i - 2].length + 1 + lines[i - 1].length + 1;

        const rows: string[][] = [];
        const rawLines = [lines[i - 2], lines[i - 1]];

        while (i < lines.length) {
          const rowLine = lines[i].trim();
          if (!rowLine.startsWith('|') || !rowLine.endsWith('|')) break;

          // Handle ragged rows — pad or trim to match header count
          const cells = splitRow(rowLine);
          const normalized = new Array(headers.length).fill('');
          for (let j = 0; j < Math.min(cells.length, headers.length); j++) {
            normalized[j] = cells[j];
          }
          rows.push(normalized);
          rawLines.push(lines[i]);
          charPos += lines[i].length + 1;
          i++;
        }

        if (rows.length > 0) {
          tables.push({
            headers,
            rows,
            rawMarkdown: rawLines.join('\n'),
            startIndex,
            endIndex: charPos,
            alignments,
            directive: lastDirective,
          });
          lastDirective = undefined;
        }
        continue;
      }
    }
    charPos += lines[i].length + 1;
    i++;
  }
  return tables;
}

// ═══════════════════════════════════════════════════════════════════
//  LAYER 2: ANALYZER
// ═══════════════════════════════════════════════════════════════════

function computeStats(nums: number[]): ColumnStats {
  if (nums.length === 0) {
    return { min: 0, max: 0, mean: 0, median: 0, sum: 0, stdDev: 0, hasNegative: false, cardinality: 0, outlierIndices: [], quartiles: [0, 0, 0], range: 0 };
  }

  const sorted = [...nums].sort((a, b) => a - b);
  const n = sorted.length;
  const sum = sorted.reduce((a, b) => a + b, 0);
  const mean = sum / n;

  const variance = sorted.reduce((acc, v) => acc + (v - mean) ** 2, 0) / n;
  const stdDev = Math.sqrt(variance);

  const q = (p: number) => {
    const pos = p * (n - 1);
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return lo === hi ? sorted[lo] : sorted[lo] * (hi - pos) + sorted[hi] * (pos - lo);
  };

  const median = q(0.5);
  const quartiles: [number, number, number] = [q(0.25), median, q(0.75)];

  const outlierIndices = nums
    .map((v, i) => (Math.abs(v - mean) > 2 * stdDev ? i : -1))
    .filter(i => i !== -1);

  const cardinality = new Set(nums).size;

  return {
    min: sorted[0],
    max: sorted[n - 1],
    mean,
    median,
    sum,
    stdDev,
    hasNegative: sorted[0] < 0,
    cardinality,
    outlierIndices,
    quartiles,
    range: sorted[n - 1] - sorted[0],
  };
}

function detectFormat(parsedValues: { format: NumericFormat }[]): NumericFormat {
  if (parsedValues.length === 0) return { prefix: '', suffix: '', decimals: 0, isCompact: false };

  // Use the most common prefix/suffix
  const prefixes = parsedValues.map(p => p.format.prefix).filter(Boolean);
  const suffixes = parsedValues.map(p => p.format.suffix).filter(Boolean);
  const maxDecimals = Math.max(0, ...parsedValues.map(p => p.format.decimals));
  const isCompact = parsedValues.some(p => p.format.isCompact);

  const mostCommon = (arr: string[]) => {
    if (arr.length === 0) return '';
    const counts = arr.reduce((m, v) => m.set(v, (m.get(v) || 0) + 1), new Map<string, number>());
    return [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
  };

  return { prefix: mostCommon(prefixes), suffix: mostCommon(suffixes), decimals: maxDecimals, isCompact };
}

/** Analyze column types and compute rich statistics */
export function analyzeColumns(table: DataTable): ColumnMeta[] {
  return table.headers.map((name, index) => {
    const values = table.rows.map(r => r[index] || '');
    const nonEmptyValues = values.filter(v => v.trim().length > 0);
    const denominator = Math.max(nonEmptyValues.length, 1);

    // Check date
    const dateCount = nonEmptyValues.filter(v => isDateLike(v)).length;
    if (dateCount / denominator >= 0.5) {
      return { name, index, type: 'date' as ColumnType, confidence: dateCount / denominator, nullCount: values.length - dateCount };
    }

    // Check ordinal
    const ordCount = nonEmptyValues.filter(v => isOrdinal(v)).length;
    const ordinalLikeIntegers = nonEmptyValues.filter(v => /^\d+$/.test(v.trim())).length;
    if (ordCount / denominator >= 0.7 || (isOrdinalHeader(name) && ordinalLikeIntegers / denominator >= 0.7)) {
      return {
        name,
        index,
        type: 'ordinal' as ColumnType,
        confidence: Math.max(ordCount / denominator, ordinalLikeIntegers / denominator),
        nullCount: values.length - Math.max(ordCount, ordinalLikeIntegers),
      };
    }

    // Check numeric
    const parsed = values.map(v => parseNumeric(v));
    const validParsed = parsed.filter((p): p is NonNullable<typeof p> => p !== null);
    const nullCount = values.length - validParsed.length;
    const confidence = validParsed.length / values.length;

    if (confidence >= 0.5 && validParsed.length >= 1) {
      const nums = validParsed.map(p => p.value);

      // Detect dominant type
      const typeCounts = validParsed.reduce((acc, p) => {
        acc[p.type] = (acc[p.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      const type = (Object.entries(typeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'number') as ColumnType;

      return {
        name, index, type, confidence, nullCount,
        stats: computeStats(nums),
        format: detectFormat(validParsed),
      };
    }

    return { name, index, type: 'string' as ColumnType, confidence: 1, nullCount: 0 };
  });
}

function isOrdinalHeader(value: string): boolean {
  return /^(rank|order|position|tier)$/i.test(value.trim());
}

/** Compute Pearson correlation between two numeric arrays */
function pearsonCorrelation(x: number[], y: number[]): number {
  const n = Math.min(x.length, y.length);
  if (n < 3) return 0;

  const meanX = x.slice(0, n).reduce((a, b) => a + b, 0) / n;
  const meanY = y.slice(0, n).reduce((a, b) => a + b, 0) / n;

  let num = 0, denX = 0, denY = 0;
  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    num += dx * dy;
    denX += dx * dx;
    denY += dy * dy;
  }

  const den = Math.sqrt(denX * denY);
  return den === 0 ? 0 : num / den;
}

/** Compute all pairwise correlations between numeric columns */
export function computeCorrelations(table: DataTable, columns: ColumnMeta[]): ColumnCorrelation[] {
  const numCols = columns.filter(c => c.stats);
  const correlations: ColumnCorrelation[] = [];

  for (let i = 0; i < numCols.length; i++) {
    for (let j = i + 1; j < numCols.length; j++) {
      const x = table.rows.map(r => parseNumeric(r[numCols[i].index])?.value ?? NaN).filter(v => !isNaN(v));
      const y = table.rows.map(r => parseNumeric(r[numCols[j].index])?.value ?? NaN).filter(v => !isNaN(v));
      const r = pearsonCorrelation(x, y);
      correlations.push({ column1: numCols[i].name, column2: numCols[j].name, r });
    }
  }

  return correlations.sort((a, b) => Math.abs(b.r) - Math.abs(a.r));
}

// ═══════════════════════════════════════════════════════════════════
//  LAYER 3: ADVISOR (Pluggable)
// ═══════════════════════════════════════════════════════════════════

export type AdvisorFn = (table: DataTable, columns: ColumnMeta[], correlations: ColumnCorrelation[]) => ChartRecommendation;

/** Format a number using detected format metadata */
export function formatValue(value: number, fmt?: NumericFormat): string {
  if (!fmt) return String(value);

  let str: string;
  if (fmt.isCompact) {
    if (Math.abs(value) >= 1e12) str = (value / 1e12).toFixed(1) + 'T';
    else if (Math.abs(value) >= 1e9) str = (value / 1e9).toFixed(1) + 'B';
    else if (Math.abs(value) >= 1e6) str = (value / 1e6).toFixed(1) + 'M';
    else if (Math.abs(value) >= 1e3) str = (value / 1e3).toFixed(1) + 'K';
    else str = value.toFixed(fmt.decimals);
  } else {
    str = value.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: fmt.decimals,
    });
  }

  return `${fmt.prefix}${str}${fmt.suffix}`;
}

const isNumericType = (t: ColumnType) => t === 'number' || t === 'currency' || t === 'percentage';

/** Default chart type advisor — production-grade heuristics */
export const defaultAdvisor: AdvisorFn = (table, columns, correlations) => {
  const numericCols = columns.filter(c => isNumericType(c.type));
  const dateCols = columns.filter(c => c.type === 'date');
  const stringCols = columns.filter(c => c.type === 'string');
  const rowCount = table.rows.length;
  const numColCount = numericCols.length;

  const labelCol = dateCols[0]?.name || stringCols[0]?.name || columns[0].name;
  const valueCols = numericCols.map(c => c.name);
  const headerLower = table.headers.map(h => h.toLowerCase());

  // ─── Quant/Finance heuristics ────────────────────────────
  
  // Detect OHLC / OHLCV
  const hasOHLC = ['open', 'high', 'low', 'close'].every(k =>
    headerLower.some(h => h.includes(k))
  );
  const hasVolume = headerLower.some(h => h.includes('volume') || h === 'vol' || h.includes(' vol'));
  if (hasOHLC) {
    return {
      type: hasVolume ? 'candlestick' : 'ohlc',
      confidence: 0.95,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: hasVolume
        ? 'OHLCV columns detected → financial candlestick chart'
        : 'OHLC columns detected without volume → OHLC bar chart',
      alternatives: hasVolume ? ['ohlc', 'line', 'area'] : ['candlestick', 'line', 'area'],
    };
  }

  // Detect cumulative return patterns
  const hasCumReturn = headerLower.some(h =>
    h.includes('cumulative') || h.includes('cum ') || h.includes('cum_') ||
    h.includes('equity') || h.includes('nav') || h.includes('portfolio value')
  );
  if (hasCumReturn && dateCols.length > 0 && rowCount > 5) {
    return {
      type: 'cumulative-return',
      confidence: 0.90,
      labelColumn: dateCols[0].name,
      valueColumns: valueCols,
      reason: 'Cumulative return/equity data → multi-line return chart',
      alternatives: ['line', 'area', 'composed'],
    };
  }

  // Detect drawdown patterns (all negative values)
  const hasDrawdown = headerLower.some(h =>
    h.includes('drawdown') || h.includes('mdd') || h.includes('max draw')
  );
  const allNegativeCol = numericCols.find(c => c.stats && c.stats.max <= 0 && c.stats.hasNegative);
  if (hasDrawdown || (allNegativeCol && numColCount <= 3 && dateCols.length > 0)) {
    return {
      type: 'drawdown',
      confidence: 0.85,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Drawdown/loss data → underwater chart',
      alternatives: ['area', 'line', 'bar'],
    };
  }

  const pnlLike = headerLower.some(h =>
    h.includes('pnl') || h.includes('p&l') || h.includes('profit') || h.includes('loss') || h.includes('alpha')
  );
  const mixedSignSingleSeries = numericCols.find(c =>
    c.stats && c.stats.hasNegative && c.stats.max > 0
  );
  if (dateCols.length > 0 && numColCount === 1 && pnlLike && mixedSignSingleSeries) {
    return {
      type: 'baseline',
      confidence: 0.9,
      labelColumn: labelCol,
      valueColumns: [mixedSignSingleSeries.name],
      reason: 'Mixed-sign profit/loss series crossing zero → baseline chart',
      alternatives: ['line', 'tv-histogram', 'area'],
    };
  }

  // Detect ML training curves (train/val/test loss, epoch-based)
  const hasLoss = headerLower.some(h =>
    h.includes('loss') || h.includes('val_loss') || h.includes('train_loss')
  );
  const hasEpoch = headerLower.some(h =>
    h.includes('epoch') || h.includes('step') || h.includes('iteration')
  );
  if (hasLoss && (hasEpoch || rowCount >= 5)) {
    return {
      type: 'loss-curve',
      confidence: 0.92,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Training loss curves detected → ML loss visualization',
      alternatives: ['line', 'area', 'composed'],
    };
  }

  // Detect predicted vs actual / forecast patterns
  const hasPredActual = headerLower.some(h =>
    h.includes('predicted') || h.includes('forecast') || h.includes('pred')
  ) && headerLower.some(h =>
    h.includes('actual') || h.includes('label') || h.includes('true') || h.includes('observed')
  );
  if (hasPredActual) {
    return {
      type: 'pred-vs-actual',
      confidence: 0.88,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Predicted vs actual columns → forecast comparison chart',
      alternatives: ['scatter', 'line', 'area'],
    };
  }

  // Detect residual patterns
  const hasResidual = headerLower.some(h =>
    h.includes('residual') || h.includes('error') || h.includes('rmse')
  );
  if (hasResidual && dateCols.length > 0 && numColCount <= 3) {
    return {
      type: 'residual',
      confidence: 0.82,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Residual/error data → residual diagnostic plot',
      alternatives: ['scatter', 'line', 'histogram'],
    };
  }

  // Detect Sharpe/metric summary (experiment result tables)
  const hasMetricSummary = headerLower.some(h =>
    h.includes('sharpe') || h.includes('oos_') || h.includes('primary_metric')
  );
  if (hasMetricSummary && numColCount >= 2 && rowCount >= 2) {
    return {
      type: 'compare',
      confidence: 0.80,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Experiment metrics → comparison view',
      alternatives: ['bar', 'radar', 'horizontal-bar'],
    };
  }

  const hasDistribution = headerLower.some(h =>
    /\bbin\b/.test(h) || h.includes('bucket') || h.includes('frequency') ||
    /\bcount\b/.test(h) || h.includes('histogram') || h.includes('distribution')
  );
  if (hasDistribution && numColCount <= 3) {
    return {
      type: 'histogram',
      confidence: 0.82,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Distribution/frequency data → histogram',
      alternatives: ['bar', 'area', 'line'],
    };
  }

  // Detect waterfall patterns (PnL breakdown, incremental)
  const hasWaterfall = headerLower.some(h =>
    h.includes('impact') || h.includes('contribution') || h.includes('attribution')
  );
  const hasMixedPosNeg = numericCols.some(c => c.stats?.hasNegative) && numColCount === 1;
  if (hasWaterfall && hasMixedPosNeg && rowCount <= 12) {
    return {
      type: 'waterfall',
      confidence: 0.80,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Attribution/impact data → waterfall chart',
      alternatives: ['bar', 'horizontal-bar', 'composed'],
    };
  }

  // Detect funnel patterns
  const hasFunnel = headerLower.some(h =>
    h.includes('stage') || h.includes('step') || h.includes('funnel') || h.includes('conversion')
  );
  if (hasFunnel && numColCount === 1 && rowCount >= 3 && rowCount <= 8) {
    const sorted = [...table.rows].map(r => parseNumeric(r[numericCols[0].index])?.value ?? 0);
    const isDescending = sorted.every((v, i) => i === 0 || v <= sorted[i - 1] * 1.1);
    if (isDescending) {
      return {
        type: 'funnel',
        confidence: 0.78,
        labelColumn: labelCol,
        valueColumns: valueCols,
        reason: 'Sequential declining values → funnel visualization',
        alternatives: ['horizontal-bar', 'bar'],
      };
    }
  }

  // ─── Standard heuristics ─────────────────────────────────

  // 1. Time series → area/line
  if (dateCols.length > 0 && rowCount > 2) {
    const hasNegative = numericCols.some(c => c.stats?.hasNegative);
    return {
      type: hasNegative ? 'line' : 'area',
      confidence: 0.92,
      labelColumn: dateCols[0].name,
      valueColumns: valueCols,
      reason: `Time-series: ${dateCols[0].name} with ${rowCount} points`,
      alternatives: ['line', 'bar', 'composed', 'area', 'cumulative-return'],
      sortBy: { column: dateCols[0].name, direction: 'asc' },
      axes: numColCount > 2 ? buildDualAxes(numericCols, dateCols[0].name) : undefined,
    };
  }

  // 2. Strong correlation between exactly 2 numeric cols → scatter
  if (numColCount === 2 && rowCount >= 5) {
    const corr = correlations.find(c =>
      (c.column1 === numericCols[0].name && c.column2 === numericCols[1].name) ||
      (c.column1 === numericCols[1].name && c.column2 === numericCols[0].name)
    );
    if (corr && Math.abs(corr.r) > 0.5) {
      return {
        type: 'scatter',
        confidence: 0.85,
        labelColumn: labelCol,
        valueColumns: valueCols,
        reason: `Strong correlation (r=${corr.r.toFixed(2)}) between ${corr.column1} × ${corr.column2}`,
        alternatives: ['line', 'bar', 'area', 'bubble'],
      };
    }
  }

  // 3. Radar: multi-dimensional comparison, few items
  if (numColCount >= 3 && rowCount >= 2 && rowCount <= 8) {
    const ranges = numericCols.map(c => c.stats?.range || 0);
    const maxRange = Math.max(...ranges);
    const minRange = Math.min(...ranges.filter(r => r > 0));
    const needsNormalize = maxRange / (minRange || 1) > 10;

    return {
      type: 'radar',
      confidence: 0.78,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: `${numColCount} dimensions × ${rowCount} items → multi-dimensional comparison`,
      alternatives: ['bar', 'composed', 'line', 'heatmap'],
      normalize: needsNormalize,
    };
  }

  // 4. Pie/donut: single value column, few rows, all positive
  if (numColCount === 1 && rowCount <= 8 && rowCount >= 2) {
    const allPositive = !numericCols[0].stats?.hasNegative;
    if (allPositive) {
      return {
        type: rowCount > 5 ? 'donut' : 'pie',
        confidence: 0.82,
        labelColumn: labelCol,
        valueColumns: valueCols,
        reason: `Single metric across ${rowCount} categories → proportion view`,
        alternatives: ['bar', 'horizontal-bar', 'donut', 'treemap'],
        sortBy: { column: valueCols[0], direction: 'desc' },
      };
    }
  }

  // 5. Composed: mixed positive/negative across multiple metrics
  const hasNegative = numericCols.some(c => c.stats?.hasNegative);
  if (hasNegative && numColCount >= 2) {
    return {
      type: 'composed',
      confidence: 0.72,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: 'Mixed positive/negative values → bar + line composition',
      alternatives: ['bar', 'line', 'area', 'waterfall'],
      axes: buildDualAxes(numericCols, labelCol),
    };
  }

  // 6. Many rows → line
  if (rowCount > 10) {
    return {
      type: 'line',
      confidence: 0.68,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: `${rowCount} data points → trend visualization`,
      alternatives: ['area', 'bar', 'composed', 'histogram'],
    };
  }

  // 7. Long labels → horizontal bar
  const avgLabelLen = table.rows.reduce((sum, r) => {
    const labelIdx = columns.findIndex(c => c.name === labelCol);
    return sum + (r[labelIdx]?.length || 0);
  }, 0) / rowCount;

  if (avgLabelLen > 15 && numColCount <= 2) {
    return {
      type: 'horizontal-bar',
      confidence: 0.65,
      labelColumn: labelCol,
      valueColumns: valueCols,
      reason: `Long category labels (avg ${Math.round(avgLabelLen)} chars) → horizontal layout`,
      alternatives: ['bar', 'line', 'pie', 'funnel'],
    };
  }

  // 8. Default: bar
  return {
    type: 'bar',
    confidence: 0.6,
    labelColumn: labelCol,
    valueColumns: valueCols,
    reason: `Categorical comparison (${rowCount} items × ${numColCount} metrics)`,
    alternatives: numColCount >= 3
      ? ['radar', 'composed', 'line', 'heatmap']
      : ['pie', 'horizontal-bar', 'line', 'treemap'],
  };
};

/** Build dual-axis config when columns have very different scales */
function buildDualAxes(numericCols: ColumnMeta[], labelCol: string): AxisConfig[] {
  if (numericCols.length < 2) return [];

  const ranges = numericCols.map(c => ({ col: c, range: c.stats?.range || 0, max: c.stats?.max || 0 }));
  ranges.sort((a, b) => b.max - a.max);

  // If the largest is 10x the smallest, suggest dual axis
  if (ranges[0].max / (ranges[ranges.length - 1].max || 1) > 5) {
    return [
      { column: ranges[0].col.name, position: 'left' },
      { column: ranges[ranges.length - 1].col.name, position: 'right' },
    ];
  }
  return [];
}

// ═══════════════════════════════════════════════════════════════════
//  PIPELINE
// ═══════════════════════════════════════════════════════════════════

export interface PipelineOptions {
  advisor?: AdvisorFn;
  /** Minimum rows for chart rendering (default: 1) */
  minRows?: number;
  /** Maximum columns to chart (default: 10) */
  maxValueColumns?: number;
}

/** Normalize records to 0-1 scale for radar charts */
export function normalizeRecords(
  records: Record<string, string | number>[],
  valueColumns: string[],
): Record<string, string | number>[] {
  const ranges = valueColumns.map(col => {
    const values = records.map(r => Number(r[col])).filter(v => !isNaN(v));
    const min = Math.min(...values);
    const max = Math.max(...values);
    return { col, min, range: max - min || 1 };
  });

  return records.map(r => {
    const nr = { ...r };
    for (const { col, min, range } of ranges) {
      nr[col] = ((Number(r[col]) - min) / range) * 100;
    }
    return nr;
  });
}

function compareDateish(left: string, right: string) {
  const normalizedLeft = normalizeDateish(left);
  const normalizedRight = normalizeDateish(right);

  if (normalizedLeft && normalizedRight) {
    return normalizedLeft.localeCompare(normalizedRight);
  }

  return left.localeCompare(right, 'en-US', {
    numeric: true,
    sensitivity: 'base',
  });
}

function normalizeDateish(value: string) {
  const trimmed = value.trim();
  if (/^\d{4}-\d{1,2}-\d{1,2}$/.test(trimmed)) {
    return trimmed
      .split('-')
      .map((part, index) => (index === 0 ? part.padStart(4, '0') : part.padStart(2, '0')))
      .join('-');
  }

  if (/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(trimmed)) {
    return trimmed
      .split('/')
      .map((part, index) => (index === 0 ? part.padStart(4, '0') : part.padStart(2, '0')))
      .join('-');
  }

  const timestamp = Date.parse(trimmed);
  if (!Number.isNaN(timestamp)) {
    return new Date(timestamp).toISOString();
  }

  return undefined;
}

/** Convert a single DataTable to chart-ready data */
export function processTable(table: DataTable, options?: PipelineOptions): ChartReadyData {
  const columns = analyzeColumns(table);
  const correlations = computeCorrelations(table, columns);
  const advisor = options?.advisor || defaultAdvisor;
  const recommendation = advisor(table, columns, correlations);

  if (table.directive?.type) {
    const originalType = recommendation.type;
    recommendation.type = table.directive.type;
    recommendation.confidence = 0.99;
    recommendation.reason = `Chart directive requested ${table.directive.type}`;
    recommendation.alternatives = [
      originalType,
      ...recommendation.alternatives.filter(type => type !== table.directive?.type && type !== originalType),
    ];
  }

  // Cap value columns
  const maxCols = options?.maxValueColumns ?? 10;
  if (recommendation.valueColumns.length > maxCols) {
    recommendation.valueColumns = recommendation.valueColumns.slice(0, maxCols);
  }

  const labelIdx = columns.find(c => c.name === recommendation.labelColumn)?.index ?? 0;
  const records = table.rows.map(row => {
    const record: Record<string, string | number> = {};
    record[recommendation.labelColumn] = row[labelIdx] || '';
    for (const colName of recommendation.valueColumns) {
      const col = columns.find(c => c.name === colName);
      if (col) {
        const parsed = parseNumeric(row[col.index] || '');
        record[colName] = parsed?.value ?? 0;
      }
    }
    return record;
  });

  // Sort if recommended
  if (recommendation.sortBy) {
    const sortCol = recommendation.sortBy.column;
    const dir = recommendation.sortBy.direction === 'asc' ? 1 : -1;
    const sortColumnMeta = columns.find(c => c.name === sortCol);
    records.sort((a, b) => {
      const av = a[sortCol];
      const bv = b[sortCol];

      if (sortColumnMeta?.type === 'date') {
        return compareDateish(String(av ?? ''), String(bv ?? '')) * dir;
      }

      if (typeof av === 'number' || typeof bv === 'number') {
        return (Number(av ?? 0) - Number(bv ?? 0)) * dir;
      }

      return String(av ?? '').localeCompare(String(bv ?? ''), 'en-US', {
        numeric: true,
        sensitivity: 'base',
      }) * dir;
    });
  }

  // Generate normalized records for radar if needed
  const normalizedRecords = recommendation.normalize
    ? normalizeRecords(records, recommendation.valueColumns)
    : undefined;

  return { table, columns, recommendation, records, normalizedRecords, correlations };
}

/** Full pipeline: markdown string → chart-ready data array */
export function processMarkdown(md: string, options?: PipelineOptions): ChartReadyData[] {
  const tables = extractTables(md);
  return tables.map(t => processTable(t, options));
}

/** Markdown segment for interleaved rendering */
export interface MarkdownSegment {
  type: 'text' | 'table';
  content: string;
  chartData?: ChartReadyData;
}

/** Split markdown into text + table segments */
export function segmentMarkdown(md: string, options?: PipelineOptions): MarkdownSegment[] {
  const tables = extractTables(md);
  if (tables.length === 0) return [{ type: 'text', content: md }];

  const segments: MarkdownSegment[] = [];
  let lastEnd = 0;

  for (const table of tables) {
    const textBefore = md.slice(lastEnd, table.startIndex).trim();
    if (textBefore) {
      segments.push({ type: 'text', content: textBefore });
    }

    const chartData = processTable(table, options);
    segments.push({ type: 'table', content: table.rawMarkdown, chartData });
    lastEnd = table.endIndex;
  }

  const textAfter = md.slice(lastEnd).trim();
  if (textAfter) {
    segments.push({ type: 'text', content: textAfter });
  }

  return segments;
}
