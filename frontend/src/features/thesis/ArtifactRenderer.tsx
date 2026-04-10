import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AreaSeries,
  CandlestickSeries,
  ColorType,
  createChart,
  LineSeries,
} from "lightweight-charts";

import type { ThesisArtifact } from "./devbox";
import { ThesisReportRenderer } from "./ThesisReportRenderer";

const proseClasses = `prose prose-invert prose-sm max-w-none 
  prose-headings:text-foreground prose-headings:font-display
  prose-p:text-muted-foreground prose-p:leading-relaxed
  prose-li:text-muted-foreground prose-li:leading-relaxed
  prose-strong:text-foreground prose-code:text-foreground`;

const tooltipStyle = {
  background: "hsl(0,0%,6%)",
  border: "1px solid hsl(0,0%,15%)",
  borderRadius: 8,
  fontSize: 12,
};

export function ArtifactRenderer({ artifact }: { artifact: ThesisArtifact }) {
  if (artifact.type === "chart_v1") {
    return <ChartArtifactRenderer artifact={artifact.data} />;
  }

  return <ThesisReportRenderer report={artifact.data} />;
}

function ChartArtifactRenderer({ artifact }: { artifact: Extract<ThesisArtifact, { type: "chart_v1" }>["data"] }) {
  return (
    <section className="space-y-4">
      <header className="space-y-2">
        <h2 className="text-xl font-display font-semibold text-foreground">{artifact.title}</h2>
        <div className={proseClasses}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{artifact.summary_markdown}</ReactMarkdown>
        </div>
      </header>

      {artifact.renderer === "lightweight" ? (
        <LightweightChartArtifactRenderer artifact={artifact} />
      ) : (
        <RechartsBarArtifactRenderer artifact={artifact} />
      )}

      <section className="rounded-xl border border-border/30 bg-background/40 p-4">
        <div className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Insights</div>
        <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
          {artifact.insights.map((insight) => (
            <li key={insight}>{insight}</li>
          ))}
        </ul>
      </section>
    </section>
  );
}

function RechartsBarArtifactRenderer({
  artifact,
}: {
  artifact: Extract<Extract<ThesisArtifact, { type: "chart_v1" }>["data"], { renderer: "recharts"; kind: "bar" }>;
}) {
  const primarySeries = artifact.series[0];

  return (
    <div className="h-[320px] w-full rounded-xl border border-border/30 bg-background/30 p-3">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={primarySeries.data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(0,0%,15%)" />
          <XAxis dataKey="label" tick={{ fill: "hsl(0,0%,40%)", fontSize: 10 }} axisLine={false} />
          <YAxis tick={{ fill: "hsl(0,0%,40%)", fontSize: 10 }} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Bar dataKey="value" fill="hsl(72, 100%, 50%)" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function LightweightChartArtifactRenderer({
  artifact,
}: {
  artifact: Extract<Extract<ThesisArtifact, { type: "chart_v1" }>["data"], { renderer: "lightweight" }>;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || container.clientWidth === 0 || container.clientHeight === 0) {
      return;
    }

    const chart = createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "hsl(0,0%,65%)",
      },
      grid: {
        vertLines: { color: "hsl(0,0%,15%)" },
        horzLines: { color: "hsl(0,0%,15%)" },
      },
      rightPriceScale: {
        borderColor: "hsl(0,0%,15%)",
      },
      timeScale: {
        borderColor: "hsl(0,0%,15%)",
      },
      crosshair: {
        vertLine: { color: "hsl(180, 80%, 50%)" },
        horzLine: { color: "hsl(180, 80%, 50%)" },
      },
    });

    if (artifact.kind === "candlestick") {
      const series = chart.addSeries(CandlestickSeries, {
        upColor: "hsl(72, 100%, 50%)",
        downColor: "hsl(0, 80%, 55%)",
        wickUpColor: "hsl(72, 100%, 50%)",
        wickDownColor: "hsl(0, 80%, 55%)",
        borderVisible: false,
      });
      series.setData(artifact.series[0].data);
    } else if (artifact.kind === "area") {
      artifact.series.forEach((entry, index) => {
        const series = chart.addSeries(AreaSeries, {
          lineColor: index === 0 ? "hsl(72, 100%, 50%)" : "hsl(180, 80%, 50%)",
          topColor: index === 0 ? "hsla(72, 100%, 50%, 0.35)" : "hsla(180, 80%, 50%, 0.3)",
          bottomColor: "hsla(0, 0%, 0%, 0)",
        });
        series.setData(entry.data);
      });
    } else {
      artifact.series.forEach((entry, index) => {
        const series = chart.addSeries(LineSeries, {
          color: index === 0 ? "hsl(72, 100%, 50%)" : "hsl(180, 80%, 50%)",
          lineWidth: 2,
        });
        series.setData(entry.data);
      });
    }

    chart.timeScale().fitContent();

    let resizeObserver: ResizeObserver | null = null;
    if (typeof ResizeObserver !== "undefined") {
      resizeObserver = new ResizeObserver((entries) => {
        const nextEntry = entries[0];
        if (!nextEntry) {
          return;
        }

        chart.applyOptions({
          width: nextEntry.contentRect.width,
          height: nextEntry.contentRect.height,
        });
        chart.timeScale().fitContent();
      });
      resizeObserver.observe(container);
    }

    return () => {
      resizeObserver?.disconnect();
      chart.remove();
    };
  }, [artifact]);

  return (
    <div className="rounded-xl border border-border/30 bg-background/30 p-3">
      <div ref={containerRef} className="h-[320px] w-full" />
    </div>
  );
}
