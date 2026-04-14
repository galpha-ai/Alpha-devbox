import type { ReactNode } from 'react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  Sparkles,
  Target,
  TrendingUp,
  XCircle,
  Zap,
} from 'lucide-react';

import { MarkdownChartRenderer } from './MarkdownChartRenderer';
import type { ThesisReportV1 } from './protocol';

const lime = 'hsl(72, 100%, 50%)';
const cyan = 'hsl(180, 80%, 50%)';
const orange = 'hsl(30, 90%, 55%)';
const red = 'hsl(0, 80%, 55%)';

const tooltipStyle = {
  background: 'hsl(0,0%,6%)',
  border: '1px solid hsl(0,0%,15%)',
  borderRadius: 8,
  fontSize: 12,
};

const proseClasses = `prose prose-invert prose-sm max-w-none 
  prose-headings:text-foreground prose-headings:font-display
  prose-h1:text-2xl prose-h1:mb-3
  prose-h2:text-xl prose-h2:mb-3
  prose-h3:text-base prose-h3:mt-6 prose-h3:mb-3
  prose-strong:text-foreground prose-table:text-xs
  prose-p:text-[hsl(var(--body-foreground))] prose-p:leading-relaxed
  prose-li:text-[hsl(var(--body-muted))] prose-li:leading-relaxed
  prose-code:text-foreground prose-code:bg-muted/40 prose-code:px-1 prose-code:py-0.5 prose-code:rounded
  prose-hr:border-border/30`;

const ChartCard = ({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) => (
  <div className="rounded-xl border border-border/30 bg-card/50 p-4">
    <h4 className="mb-3 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
      {title}
    </h4>
    {children}
  </div>
);

export function ThesisReportRenderer({ report }: { report: ThesisReportV1 }) {
  return (
    <div className="space-y-6">
      <section className="space-y-3 rounded-2xl border border-border/40 bg-card/35 p-5">
        <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-primary/80">
          <FlaskConical className="h-3.5 w-3.5" />
          Thesis Report
        </div>
        <div>
          <h1 className="text-2xl font-display font-semibold text-foreground sm:text-3xl">
            {report.title}
          </h1>
        </div>
        <div className={proseClasses}>
          <MarkdownChartRenderer
            markdown={report.summary_markdown}
            variant="compact"
          />
        </div>
      </section>

      <StatsRow report={report} />

      <div className="grid gap-6 xl:grid-cols-[1.65fr_1fr]">
        <div className="space-y-6">
          <PnlChart report={report} />
          <SecondaryChart report={report} />
          <WhyItWorks report={report} />
          <VerdictCard report={report} />
        </div>

        <div className="space-y-6">
          <KeyMetricsTable report={report} />
          <MonteCarloTable report={report} />
          <SensitivityTable report={report} />
          <EconomicsCards report={report} />
          <AssumptionsCard report={report} />
        </div>
      </div>

      <DisclaimerCard report={report} />
    </div>
  );
}

function StatsRow({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {report.stats.map((stat) => (
        <div
          key={`${stat.label}-${stat.value}`}
          className="rounded-xl border border-border/35 bg-card/50 p-4"
        >
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
            {stat.label}
          </div>
          <div className="mt-2 text-xl font-semibold text-foreground">
            {stat.value}
          </div>
          {stat.sub && (
            <div className="mt-1 text-xs text-muted-foreground">{stat.sub}</div>
          )}
        </div>
      ))}
    </section>
  );
}

function PnlChart({ report }: { report: ThesisReportV1 }) {
  return (
    <ChartCard title="Cumulative P&L Curve">
      <div className="h-[220px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={report.pnl_series}>
            <defs>
              <linearGradient id="pnl-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={lime} stopOpacity={0.35} />
                <stop offset="100%" stopColor={lime} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
            <XAxis
              dataKey="x"
              tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
              axisLine={false}
            />
            <YAxis
              tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
              axisLine={false}
            />
            <Tooltip contentStyle={tooltipStyle} />
            <Area
              type="monotone"
              dataKey="pnl"
              stroke={lime}
              fill="url(#pnl-grad)"
              strokeWidth={2}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}

function SecondaryChart({ report }: { report: ThesisReportV1 }) {
  const chart = report.secondary_chart;

  if (chart.kind === 'drawdown') {
    return (
      <ChartCard title="Drawdown Profile">
        <div className="h-[220px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chart.series}>
              <defs>
                <linearGradient id="drawdown-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={red} stopOpacity={0} />
                  <stop offset="100%" stopColor={red} stopOpacity={0.3} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
              <XAxis
                dataKey="x"
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
              />
              <YAxis
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Area
                type="monotone"
                dataKey="value"
                stroke={red}
                fill="url(#drawdown-grad)"
                strokeWidth={2}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>
    );
  }

  if (chart.kind === 'winprob') {
    return (
      <ChartCard title="Win Probability Path">
        <div className="h-[220px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chart.series}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
              <XAxis
                dataKey="x"
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
              />
              <YAxis
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
                domain={[0, 100]}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Line
                type="monotone"
                dataKey="primary"
                stroke={lime}
                strokeWidth={2}
                dot={false}
                name="Primary"
              />
              <Line
                type="monotone"
                dataKey="secondary"
                stroke={orange}
                strokeWidth={2}
                dot={false}
                name="Secondary"
                strokeDasharray="4 4"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>
    );
  }

  if (chart.kind === 'spread') {
    return (
      <ChartCard title="Spread Snapshot">
        <div className="h-[220px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart.series} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
              <XAxis
                type="number"
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                tick={{ fill: 'hsl(0,0%,40%)', fontSize: 10 }}
                axisLine={false}
                width={90}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chart.series.map((point) => (
                  <Cell
                    key={point.label}
                    fill={
                      point.value < 0
                        ? lime
                        : point.value > 0
                          ? red
                          : 'hsl(0,0%,35%)'
                    }
                    fillOpacity={0.75}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>
    );
  }

  if (chart.kind === 'correlation') {
    return (
      <ChartCard title="Pair Correlation & Spread">
        <div className="space-y-3">
          {chart.series.map((point) => (
            <div key={point.label} className="flex items-center gap-3">
              <span className="w-24 shrink-0 font-mono text-xs text-muted-foreground">
                {point.label}
              </span>
              <div className="relative h-6 flex-1 overflow-hidden rounded-full bg-muted/30">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-primary/60 to-primary"
                  style={{
                    width: `${Math.max(0, Math.min(100, point.value * 100))}%`,
                  }}
                />
                <span className="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-foreground">
                  rho = {point.value}
                </span>
              </div>
              <span className="w-14 text-right text-[10px] text-muted-foreground">
                z = {point.secondary}
              </span>
            </div>
          ))}
        </div>
      </ChartCard>
    );
  }

  return null;
}

function KeyMetricsTable({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="overflow-hidden rounded-xl border border-border/35 bg-card/45">
      <div className="flex items-center gap-2 border-b border-border/25 bg-card/75 px-4 py-3">
        <BarChart3 className="h-4 w-4 text-primary" />
        <span className="text-xs font-medium text-foreground">Key Numbers</span>
      </div>
      <div className="divide-y divide-border/15">
        {report.key_metrics.map((metric) => (
          <div
            key={`${metric.metric}-${metric.value}`}
            className="flex items-center justify-between gap-4 px-4 py-3"
          >
            <span className="text-sm text-muted-foreground">
              {metric.metric}
            </span>
            <div className="text-right">
              <div
                className={`text-sm font-medium ${metric.highlight ? (metric.positive ? 'text-primary' : 'text-destructive') : 'text-foreground'}`}
              >
                {metric.value}
              </div>
              {metric.sub && (
                <div className="text-[10px] text-muted-foreground/70">
                  {metric.sub}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function MonteCarloTable({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="overflow-hidden rounded-xl border border-border/35 bg-card/45">
      <div className="flex items-center gap-2 border-b border-border/25 bg-card/75 px-4 py-3">
        <CheckCircle2 className="h-4 w-4 text-primary" />
        <span className="text-xs font-medium text-foreground">
          Monte Carlo Robustness
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="border-b border-border/25">
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">
                Metric
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Mean
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Std
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Min
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Max
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/15">
            {report.monte_carlo_table.map((row) => (
              <tr key={row.metric}>
                <td className="px-4 py-2 text-muted-foreground">
                  {row.metric}
                </td>
                <td className="px-3 py-2 text-right font-medium text-foreground">
                  {row.mean}
                </td>
                <td className="px-3 py-2 text-right text-muted-foreground">
                  {row.std}
                </td>
                <td className="px-3 py-2 text-right text-muted-foreground">
                  {row.min}
                </td>
                <td className="px-3 py-2 text-right text-muted-foreground">
                  {row.max}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SensitivityTable({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="overflow-hidden rounded-xl border border-border/35 bg-card/45">
      <div className="flex items-center gap-2 border-b border-border/25 bg-card/75 px-4 py-3">
        <Activity className="h-4 w-4 text-primary" />
        <span className="text-xs font-medium text-foreground">
          Parameter Sensitivity
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] text-sm">
          <thead>
            <tr className="border-b border-border/25">
              <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">
                Scenario
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Win%
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Avg PnL
              </th>
              <th className="px-3 py-2 text-right text-xs font-medium text-muted-foreground">
                Total PnL
              </th>
              <th className="w-8 px-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-border/15">
            {report.sensitivity.map((row) => (
              <tr key={row.scenario}>
                <td className="px-4 py-2.5 text-muted-foreground">
                  {row.scenario}
                </td>
                <td className="px-3 py-2.5 text-right text-foreground">
                  {row.win}
                </td>
                <td
                  className={`px-3 py-2.5 text-right font-medium ${row.avg_pnl.startsWith('-') ? 'text-destructive' : 'text-primary'}`}
                >
                  {row.avg_pnl}
                </td>
                <td
                  className={`px-3 py-2.5 text-right font-medium ${row.total_pnl.startsWith('-') ? 'text-destructive' : 'text-primary'}`}
                >
                  {row.total_pnl}
                </td>
                <td className="px-2 py-2.5 text-center">
                  {row.tag === 'best' && (
                    <Sparkles className="inline h-3.5 w-3.5 text-yellow-400" />
                  )}
                  {row.tag === 'danger' && (
                    <XCircle className="inline h-3.5 w-3.5 text-destructive" />
                  )}
                  {row.tag === 'baseline' && (
                    <Target className="inline h-3.5 w-3.5 text-muted-foreground" />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function WhyItWorks({ report }: { report: ThesisReportV1 }) {
  const icons = [TrendingUp, Zap, Activity];

  return (
    <section className="space-y-3">
      <h2 className="text-base font-display font-semibold text-foreground">
        Why It Works
      </h2>
      <div className="grid gap-3 sm:grid-cols-3">
        {report.reasons.map((reason, index) => {
          const Icon = icons[index % icons.length];
          return (
            <article
              key={reason.title}
              className="rounded-xl border border-border/35 bg-card/45 p-4"
            >
              <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg border border-primary/20 bg-primary/10">
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="text-sm font-medium text-foreground">
                {reason.title}
              </div>
              <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                {reason.desc}
              </p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function EconomicsCards({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-display font-semibold text-foreground">
        Economics
      </h2>
      <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
        {report.economics.map((entry) => (
          <article
            key={entry.label}
            className="rounded-xl border border-border/35 bg-card/45 p-4 text-center"
          >
            <div className="text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
              {entry.label}
            </div>
            <div className="mt-2 text-lg font-semibold text-primary">
              {entry.pnl}
            </div>
            <div className="mt-1 text-xs text-muted-foreground">
              {entry.size}
            </div>
            <ArrowUpRight className="mx-auto mt-2 h-3.5 w-3.5 text-primary/60" />
          </article>
        ))}
      </div>
    </section>
  );
}

function VerdictCard({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="rounded-xl border border-primary/30 bg-primary/5 p-4">
      <div className="flex items-center gap-2">
        <CheckCircle2 className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold text-foreground">Verdict</span>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        {report.verdict}
      </p>
    </section>
  );
}

function AssumptionsCard({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="rounded-xl border border-border/35 bg-card/45 p-4">
      <h2 className="text-sm font-semibold text-foreground">Assumptions</h2>
      <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
        {report.assumptions.length > 0 ? (
          report.assumptions.map((assumption) => (
            <li key={assumption}>• {assumption}</li>
          ))
        ) : (
          <li>• No explicit assumptions provided.</li>
        )}
      </ul>
    </section>
  );
}

function DisclaimerCard({ report }: { report: ThesisReportV1 }) {
  return (
    <section className="rounded-xl border border-border/30 bg-card/35 p-4 text-xs leading-relaxed text-muted-foreground">
      <span className="font-medium text-foreground">Disclaimer</span>
      <p className="mt-2">{report.disclaimer}</p>
    </section>
  );
}
