import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { SmartChart } from "./BetterMarkdownSmartChart";
import { segmentMarkdown } from "./mdCharts";

type RenderVariant = "default" | "compact";

interface MarkdownChartRendererProps {
  markdown: string;
  proseClassName?: string;
  variant?: RenderVariant;
}

export function MarkdownChartRenderer({
  markdown,
  proseClassName,
  variant = "default",
}: MarkdownChartRendererProps) {
  const segments = useMemo(() => segmentMarkdown(markdown), [markdown]);
  const compact = variant === "compact";
  const chartHeight = compact ? 240 : 300;

  return (
    <div className={compact ? "space-y-2" : "space-y-4"}>
      {segments.map((segment, index) => {
        if (segment.type === "text") {
          return (
            <div key={`text-${index}`} className={proseClassName}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(variant)}>
                {segment.content}
              </ReactMarkdown>
            </div>
          );
        }

        const chartData = segment.chartData;

        if (!chartData || chartData.recommendation.valueColumns.length === 0) {
          return (
            <div key={`table-${index}`} className={proseClassName}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(variant)}>
                {segment.content}
              </ReactMarkdown>
            </div>
          );
        }

        return (
          <div key={`chart-${index}`} className={compact ? "space-y-2" : "space-y-3"}>
            <div className={proseClassName}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={createMarkdownComponents(variant)}>
                {segment.content}
              </ReactMarkdown>
            </div>
            <SmartChart
              data={chartData}
              height={chartHeight}
              interactive
              className={`border border-border bg-card ${compact ? "rounded-md p-3" : "rounded-lg p-4"}`}
            />
          </div>
        );
      })}
    </div>
  );
}

function createMarkdownComponents(variant: RenderVariant) {
  const compact = variant === "compact";

  return {
    table: ({ children }: React.ComponentProps<"table">) => (
      <div className={`overflow-x-auto border border-border ${compact ? "rounded-md" : "rounded-lg"}`}>
        <table className={`w-full text-foreground ${compact ? "text-xs" : "text-sm"}`}>{children}</table>
      </div>
    ),
    th: ({ children }: React.ComponentProps<"th">) => (
      <th className={`border-b border-border bg-secondary/50 text-left text-xs font-semibold text-muted-foreground ${compact ? "px-2 py-1.5" : "px-3 py-2"}`}>
        {children}
      </th>
    ),
    td: ({ children }: React.ComponentProps<"td">) => (
      <td className={`border-b border-border/50 ${compact ? "px-2 py-1.5 text-xs" : "px-3 py-2 text-sm"}`}>{children}</td>
    ),
    h1: ({ children }: React.ComponentProps<"h1">) => <h1 className={`${compact ? "text-xl" : "text-2xl"} font-bold text-foreground`}>{children}</h1>,
    h2: ({ children }: React.ComponentProps<"h2">) => <h2 className={`${compact ? "text-lg" : "text-xl"} font-semibold text-foreground`}>{children}</h2>,
    h3: ({ children }: React.ComponentProps<"h3">) => <h3 className={`${compact ? "text-base" : "text-lg"} font-medium text-foreground`}>{children}</h3>,
    p: ({ children }: React.ComponentProps<"p">) => <p className={`${compact ? "text-xs" : "text-sm"} leading-relaxed text-muted-foreground`}>{children}</p>,
    strong: ({ children }: React.ComponentProps<"strong">) => <strong className="font-semibold text-foreground">{children}</strong>,
    li: ({ children }: React.ComponentProps<"li">) => <li className={`${compact ? "text-xs" : "text-sm"} text-muted-foreground`}>{children}</li>,
    blockquote: ({ children }: React.ComponentProps<"blockquote">) => (
      <blockquote className={`border-l-2 border-primary/30 ${compact ? "pl-3 text-xs" : "pl-4 text-sm"} italic text-muted-foreground`}>{children}</blockquote>
    ),
    code: ({
      children,
      className,
    }: React.ComponentProps<"code"> & { className?: string }) => {
      if (className?.includes("language-")) {
        return (
          <code className={`code-block block overflow-x-auto rounded-lg text-foreground ${compact ? "p-3 text-xs" : "p-4 text-sm"}`}>
            {children}
          </code>
        );
      }

      return (
        <code className={`rounded bg-secondary font-mono text-primary ${compact ? "px-1 py-0.5 text-xs" : "px-1.5 py-0.5 text-sm"}`}>
          {children}
        </code>
      );
    },
    pre: ({ children }: React.ComponentProps<"pre">) => <pre className="code-block overflow-hidden rounded-lg">{children}</pre>,
  };
}
