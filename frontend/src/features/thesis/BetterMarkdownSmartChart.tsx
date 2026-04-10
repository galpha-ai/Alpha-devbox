import { useCallback, useState, Component, type ReactNode } from 'react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  PieChart, Pie, Cell, ComposedChart, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ReferenceLine, Treemap as RechartTreemap, FunnelChart, Funnel,
} from 'recharts';
import type { ChartReadyData, NumericFormat } from './mdCharts';
import { formatValue } from './mdCharts';

type ChartType = string;

// ─── Theme ──────────────────────────────────────────────────────────

const PALETTES = {
  default: [
    'hsl(142 72% 50%)', 'hsl(210 100% 60%)', 'hsl(262 83% 65%)',
    'hsl(38 92% 55%)', 'hsl(186 100% 42%)', 'hsl(0 72% 56%)',
    'hsl(330 80% 60%)', 'hsl(60 70% 50%)',
  ],
  warm: [
    'hsl(0 72% 56%)', 'hsl(25 90% 55%)', 'hsl(38 92% 55%)',
    'hsl(50 85% 50%)', 'hsl(330 80% 60%)', 'hsl(280 65% 55%)',
  ],
  cool: [
    'hsl(210 100% 60%)', 'hsl(186 100% 42%)', 'hsl(142 72% 50%)',
    'hsl(262 83% 65%)', 'hsl(230 70% 55%)', 'hsl(170 65% 45%)',
  ],
} as const;

export type ColorPalette = keyof typeof PALETTES;

export interface ChartTheme {
  palette?: ColorPalette | string[];
  gridColor?: string;
  textColor?: string;
  tooltipBg?: string;
  tooltipBorder?: string;
  animationDuration?: number;
}

const defaultTheme: Required<ChartTheme> = {
  palette: 'default',
  gridColor: 'hsl(220 14% 14%)',
  textColor: 'hsl(215 14% 50%)',
  tooltipBg: 'hsl(220 14% 7%)',
  tooltipBorder: 'hsl(220 14% 16%)',
  animationDuration: 800,
};

function getColors(theme: ChartTheme): string[] {
  const p = theme.palette || 'default';
  if (Array.isArray(p)) return p;
  return [...(PALETTES[p] || PALETTES.default)];
}

const CHART_TYPE_LABELS: Record<string, string> = {
  "horizontal-bar": "Horizontal Bar",
  "stacked-bar": "Stacked Bar",
  "tv-line": "TradingView Line",
  "tv-area": "TradingView Area",
  "tv-histogram": "TradingView Histogram",
  "cumulative-return": "Cumulative Return",
  "equity-curve": "Equity Curve",
  drawdown: "Drawdown",
  "pred-vs-actual": "Predicted vs Actual",
  "loss-curve": "Loss Curve",
  "metric-summary": "Metric Summary",
  "volume-profile": "Volume Profile",
};

function formatChartTypeLabel(type: string): string {
  if (CHART_TYPE_LABELS[type]) return CHART_TYPE_LABELS[type];

  return type
    .split("-")
    .map((part) => {
      if (part === "ohlc") return "OHLC";
      if (part === "pnl") return "PnL";
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(" ");
}


// ─── Error Boundary ─────────────────────────────────────────────────

interface ErrorBoundaryState { hasError: boolean; error?: Error }

export class ChartErrorBoundary extends Component<{ children: ReactNode; fallback?: ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          <p className="font-medium">Chart rendering failed</p>
          <p className="text-xs mt-1 text-muted-foreground">{this.state.error?.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

// ─── Tooltip Formatter ──────────────────────────────────────────────

function SmartTooltip({
  active,
  payload,
  label,
  formats,
}: {
  active?: boolean;
  payload?: Array<{ dataKey: string; value: number; color: string }>;
  label?: string;
  formats?: Record<string, NumericFormat>;
}) {
  if (!active || !payload?.length) return null;

  return (
    <div className="rounded-lg border border-border bg-card p-3 shadow-lg text-sm">
      <p className="font-medium text-foreground mb-1.5">{label}</p>
      {payload.map((entry, i: number) => {
        const fmt = formats?.[entry.dataKey];
        const formatted = fmt ? formatValue(entry.value, fmt) : entry.value?.toLocaleString();
        return (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-muted-foreground">{entry.dataKey}:</span>
            <span className="font-medium text-foreground">{formatted}</span>
          </div>
        );
      })}
    </div>
  );
}

// ─── Main Component ─────────────────────────────────────────────────

interface SmartChartProps {
  data: ChartReadyData;
  height?: number;
  theme?: ChartTheme;
  interactive?: boolean;
  className?: string;
}

const FALLBACK_RENDER_TYPES = new Set<ChartType>([
  'bar',
  'horizontal-bar',
  'stacked-bar',
  'line',
  'cumulative-return',
  'equity-curve',
  'loss-curve',
  'pred-vs-actual',
  'residual',
  'timeline',
  'compare',
  'metric-summary',
  'area',
  'drawdown',
  'waterfall',
  'histogram',
  'distribution',
  'heatmap',
  'radar',
  'pie',
  'donut',
  'scatter',
  'bubble',
  'funnel',
  'treemap',
  'composed',
]);

export function SmartChart({
  data, height = 300, theme: userTheme, interactive = true,
  className = '',
}: SmartChartProps) {
  const { recommendation, records, normalizedRecords, columns } = data;
  const [activeType, setActiveType] = useState<ChartType | undefined>(undefined);

  const type = activeType || recommendation.type;
  const { labelColumn, valueColumns } = recommendation;
  const theme = { ...defaultTheme, ...userTheme };
  const colors = getColors(theme);

  const formatMap: Record<string, NumericFormat> = {};
  for (const col of columns) {
    if (col.format) formatMap[col.name] = col.format;
  }

  const chartRecords = (type === 'radar' && normalizedRecords) ? normalizedRecords : records;
  const switchType = useCallback((chartType: ChartType) => {
    setActiveType(chartType === recommendation.type ? undefined : chartType);
  }, [recommendation.type]);

  const rawTypes = [recommendation.type, ...recommendation.alternatives.filter((chartType) => chartType !== recommendation.type)];
  const seen = new Set<string>();
  const allTypes: ChartType[] = [];
  for (const chartType of rawTypes) {
    if (FALLBACK_RENDER_TYPES.has(chartType) && !seen.has(chartType)) {
      seen.add(chartType);
      allTypes.push(chartType);
    }
  }

  return (
    <ChartErrorBoundary>
      <div className={`rounded-lg border border-border bg-card p-4 space-y-3 animate-fade-in ${className}`}>
        {interactive && allTypes.length > 1 && (
          <div className="flex items-center gap-1 flex-wrap">
            {allTypes.map((chartType) => (
              <button
                key={chartType}
                type="button"
                onClick={() => switchType(chartType)}
                className={`text-[11px] px-2 py-0.5 rounded transition-all ${
                  type === chartType
                    ? 'bg-primary/15 text-primary font-medium'
                    : 'bg-secondary/50 text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
              >
                {formatChartTypeLabel(chartType)}
              </button>
            ))}
          </div>
        )}
        {(() => {
          return (
            <ResponsiveContainer width="100%" height={height}>
              {renderChart(type, chartRecords, labelColumn, valueColumns, colors, theme, formatMap)}
            </ResponsiveContainer>
          );
        })()}
      </div>
    </ChartErrorBoundary>
  );
}

// ─── Chart Renderer ─────────────────────────────────────────────────

function renderChart(
  type: ChartType,
  data: Record<string, string | number>[],
  labelColumn: string,
  valueColumns: string[],
  colors: string[],
  theme: Required<ChartTheme>,
  formats: Record<string, NumericFormat>,
) {
  const axisProps = { tick: { fill: theme.textColor, fontSize: 12 }, axisLine: { stroke: theme.gridColor } };
  const grid = <CartesianGrid strokeDasharray="3 3" stroke={theme.gridColor} />;
  const xAxis = <XAxis dataKey={labelColumn} {...axisProps} interval={0} angle={data.length > 6 ? -30 : 0} textAnchor={data.length > 6 ? 'end' : 'middle'} height={data.length > 6 ? 60 : 30} />;
  const yAxis = <YAxis {...axisProps} width={60} />;
  const tooltip = <Tooltip content={<SmartTooltip formats={formats} />} />;
  const legend = <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />;
  const anim = { animationDuration: theme.animationDuration, animationEasing: 'ease-out' as const };

  switch (type) {
    case 'bar':
    case 'compare':
    case 'metric-summary':
      return (
        <BarChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          {valueColumns.map((col, i) => (
            <Bar key={col} dataKey={col} fill={colors[i % colors.length]} radius={[4, 4, 0, 0]} {...anim} />
          ))}
        </BarChart>
      );

    case 'horizontal-bar':
      return (
        <BarChart data={data} layout="vertical">
          {grid}
          <XAxis type="number" {...axisProps} />
          <YAxis type="category" dataKey={labelColumn} {...axisProps} width={120} />
          {tooltip}{legend}
          {valueColumns.map((col, i) => (
            <Bar key={col} dataKey={col} fill={colors[i % colors.length]} radius={[0, 4, 4, 0]} {...anim} />
          ))}
        </BarChart>
      );

    case 'stacked-bar':
      return (
        <BarChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          {valueColumns.map((col, i) => (
            <Bar key={col} dataKey={col} fill={colors[i % colors.length]} stackId="stack" {...anim} />
          ))}
        </BarChart>
      );

    case 'line':
    case 'cumulative-return':
    case 'equity-curve':
    case 'loss-curve':
    case 'pred-vs-actual':
    case 'residual':
    case 'timeline':
      return (
        <LineChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          <ReferenceLine y={0} stroke={theme.gridColor} strokeDasharray="3 3" />
          {valueColumns.map((col, i) => (
            <Line key={col} type="monotone" dataKey={col} stroke={colors[i % colors.length]}
              strokeWidth={2} dot={data.length > 20 ? false : { r: 3, strokeWidth: 2 }} activeDot={{ r: 5 }} {...anim} />
          ))}
        </LineChart>
      );

    case 'area':
      return (
        <AreaChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          {valueColumns.map((col, i) => (
            <Area key={col} type="monotone" dataKey={col} stroke={colors[i % colors.length]}
              fill={colors[i % colors.length]} fillOpacity={0.12} strokeWidth={2} {...anim} />
          ))}
        </AreaChart>
      );

    case 'drawdown':
      return (
        <AreaChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          <ReferenceLine y={0} stroke={theme.textColor} strokeWidth={1} />
          {valueColumns.map((col, i) => (
            <Area key={col} type="monotone" dataKey={col}
              stroke={colors[i % colors.length] || 'hsl(0 72% 56%)'}
              fill={colors[i % colors.length] || 'hsl(0 72% 56%)'}
              fillOpacity={0.25} strokeWidth={2} {...anim} />
          ))}
        </AreaChart>
      );

    case 'waterfall': {
      return (
        <BarChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          <ReferenceLine y={0} stroke={theme.textColor} />
          {valueColumns.map((col) => (
            <Bar key={col} dataKey={col} radius={[4, 4, 0, 0]} {...anim}>
              {data.map((d, j) => {
                const val = Number(d[col]) || 0;
                return <Cell key={j} fill={val >= 0 ? 'hsl(142 72% 50%)' : 'hsl(0 72% 56%)'} />;
              })}
            </Bar>
          ))}
        </BarChart>
      );
    }

    case 'histogram':
    case 'distribution':
      return (
        <BarChart data={data} barGap={0} barCategoryGap={0}>
          {grid}{xAxis}{yAxis}{tooltip}
          {valueColumns.map((col, i) => (
            <Bar key={col} dataKey={col} fill={colors[i % colors.length]} fillOpacity={0.7} {...anim} />
          ))}
          {legend}
        </BarChart>
      );

    case 'heatmap':
      return (
        <BarChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          {valueColumns.map((col, i) => (
            <Bar key={col} dataKey={col} fill={colors[i % colors.length]} stackId="heatmap" {...anim} />
          ))}
        </BarChart>
      );

    case 'radar':
      return (
        <RadarChart data={data}>
          <PolarGrid stroke={theme.gridColor} />
          <PolarAngleAxis dataKey={labelColumn} tick={{ fill: theme.textColor, fontSize: 11 }} />
          <PolarRadiusAxis tick={{ fill: theme.textColor, fontSize: 10 }} />
          {valueColumns.map((col, i) => (
            <Radar key={col} dataKey={col} stroke={colors[i % colors.length]}
              fill={colors[i % colors.length]} fillOpacity={0.15} {...anim} />
          ))}
          {legend}{tooltip}
        </RadarChart>
      );

    case 'pie':
    case 'donut':
      return (
        <PieChart>
          <Pie
            data={data} dataKey={valueColumns[0]} nameKey={labelColumn}
            cx="50%" cy="50%"
            innerRadius={type === 'donut' ? 50 : 0}
            outerRadius={100}
            label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
            labelLine={{ stroke: theme.textColor }}
            {...anim}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Pie>
          {tooltip}
        </PieChart>
      );

    case 'scatter':
    case 'bubble':
      return (
        <ScatterChart>
          {grid}
          <XAxis dataKey={valueColumns[0]} name={valueColumns[0]} {...axisProps} type="number" />
          <YAxis dataKey={valueColumns[1]} name={valueColumns[1]} {...axisProps} type="number" />
          {tooltip}{legend}
          <Scatter name={`${valueColumns[0]} vs ${valueColumns[1]}`} data={data} fill={colors[0]} {...anim}>
            {data.map((_, i) => (
              <Cell key={i} fill={colors[i % colors.length]} />
            ))}
          </Scatter>
        </ScatterChart>
      );

    case 'funnel':
      try {
        return (
          <FunnelChart>
            {tooltip}{legend}
            <Funnel
              data={data.map((d, i) => ({
                name: String(d[labelColumn]),
                value: Number(d[valueColumns[0]]) || 0,
                fill: colors[i % colors.length],
              }))}
              dataKey="value"
              nameKey="name"
              {...anim}
            />
          </FunnelChart>
        );
      } catch {
        return renderChart('horizontal-bar', data, labelColumn, valueColumns, colors, theme, formats);
      }

    case 'treemap':
      try {
        const treemapData = data.map((d, i) => ({
          name: String(d[labelColumn]),
          size: Number(d[valueColumns[0]]) || 0,
          fill: colors[i % colors.length],
        }));
        return (
          <RechartTreemap
            data={treemapData}
            dataKey="size"
            nameKey="name"
            aspectRatio={4 / 3}
            stroke={theme.gridColor}
            {...anim}
          />
        );
      } catch {
        return renderChart('bar', data, labelColumn, valueColumns, colors, theme, formats);
      }

    case 'composed':
    default:
      return (
        <ComposedChart data={data}>
          {grid}{xAxis}{yAxis}{tooltip}{legend}
          <ReferenceLine y={0} stroke={theme.gridColor} strokeDasharray="3 3" />
          {valueColumns.map((col, i) => (
            i === 0
              ? <Bar key={col} dataKey={col} fill={colors[i % colors.length]} radius={[4, 4, 0, 0]} {...anim} />
              : <Line key={col} type="monotone" dataKey={col} stroke={colors[i % colors.length]} strokeWidth={2} dot={{ r: 3 }} {...anim} />
          ))}
        </ComposedChart>
      );
  }
}
