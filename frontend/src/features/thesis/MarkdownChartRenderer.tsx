import { MarkdownChartRenderer as BetterMarkdownRenderer } from '@galpha-ai/better-markdown/react';

type RenderVariant = 'default' | 'compact';

interface MarkdownChartRendererProps {
  markdown: string;
  proseClassName?: string;
  variant?: RenderVariant;
}

export function MarkdownChartRenderer({
  markdown,
  proseClassName,
  variant = 'default',
}: MarkdownChartRendererProps) {
  const chartHeight = variant === 'compact' ? 240 : 300;

  return (
    <div
      className={`min-w-0 max-w-full overflow-x-auto ${proseClassName ?? ''}`.trim()}
    >
      <BetterMarkdownRenderer
        markdown={markdown}
        chartHeight={chartHeight}
        interactive
        variant={variant}
      />
    </div>
  );
}
