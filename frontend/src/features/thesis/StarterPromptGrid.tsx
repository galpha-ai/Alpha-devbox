import {
  Activity,
  FlaskConical,
  BarChart2,
  GitCompareArrows,
  TrendingUp,
} from 'lucide-react';
import btcImg from '@/assets/thesis/btc-momentum.jpg';
import sp500Img from '@/assets/thesis/sp500-reversion.jpg';
import nbaImg from '@/assets/thesis/nba-prediction.jpg';
import pairsImg from '@/assets/thesis/pairs-trading.jpg';

const STARTER_CARDS = [
  {
    title: 'NBA Prediction',
    prompt:
      'backtest the strategy not on oil price, but on NBA game; where in the first 70% time of the NBA game before the game end, enter the trade when the ratio move from the initial bigger gap when a NBA game start, to getting close to between 50:50 and 60:40; then you buy into the strong prior of the team which stronger win rate; exit when the ratio move into 70:30 or above',
    icon: Activity,
    img: nbaImg,
    accent: 'from-orange-500/20',
  },
  {
    title: 'BTC Momentum',
    prompt: 'Backtest a momentum strategy on BTC',
    icon: TrendingUp,
    img: btcImg,
    accent: 'from-green-500/20',
  },
  {
    title: 'S&P 500 Reversion',
    prompt: 'Mean reversion on S&P 500 sectors',
    icon: BarChart2,
    img: sp500Img,
    accent: 'from-cyan-500/20',
  },
  {
    title: 'Pairs Trading',
    prompt: 'Pairs trading on tech stocks',
    icon: GitCompareArrows,
    img: pairsImg,
    accent: 'from-purple-500/20',
  },
] as const;

export function StarterPromptGrid({
  disabled,
  onSelectPrompt,
}: {
  disabled?: boolean;
  onSelectPrompt: (prompt: string, title: string) => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-8 px-4 py-6">
      <div className="max-w-md space-y-3 text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl border border-primary/20 bg-primary/10">
          <FlaskConical className="h-7 w-7 text-primary" />
        </div>
        <h2 className="text-2xl font-display font-semibold text-foreground">Starter Prompts</h2>
        <p className="text-sm leading-relaxed text-muted-foreground">
          Choose a prompt to create a conversation and iterate in chat.
        </p>
      </div>

      <div className="grid w-full max-w-xl grid-cols-1 gap-3 md:grid-cols-2">
        {STARTER_CARDS.map((starter) => {
          const Icon = starter.icon;

          return (
            <button
              key={starter.title}
              type="button"
              disabled={disabled}
              onClick={() => onSelectPrompt(starter.prompt, starter.title)}
              className="group relative overflow-hidden rounded-xl border border-border/40 text-left transition-all hover:border-primary/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <div className="absolute inset-0">
                <img
                  src={starter.img}
                  alt=""
                  className="h-full w-full object-cover opacity-40 transition-all duration-500 group-hover:scale-110 group-hover:opacity-60"
                  loading="lazy"
                  width={768}
                  height={512}
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${starter.accent} via-background/80 to-background`} />
              </div>
              <div className="relative space-y-1.5 p-4 pt-16">
                <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-border/40 bg-card/80 backdrop-blur-sm">
                  <Icon className="h-3.5 w-3.5 text-primary" />
                </div>
                <div className="text-sm font-medium text-foreground">{starter.title}</div>
                <p className="line-clamp-2 text-[11px] leading-relaxed text-muted-foreground">{starter.prompt}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
