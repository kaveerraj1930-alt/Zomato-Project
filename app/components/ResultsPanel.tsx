'use client';

import { SummaryData } from '../../lib/api';

interface ResultsPanelProps {
  data: SummaryData | null;
  loading: boolean;
}

function StarRating({ rating }: { rating: number }) {
  const full = Math.floor(rating);
  const half = rating - full >= 0.5;
  return (
    <span className="text-amber-400 text-sm tracking-wide" title={`${rating.toFixed(1)} / 5`}>
      {'★'.repeat(full)}
      {half ? '½' : ''}
      {'☆'.repeat(5 - full - (half ? 1 : 0))}
    </span>
  );
}

export default function ResultsPanel({ data, loading }: ResultsPanelProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-5 w-40 animate-pulse rounded-lg bg-slate-200" />
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="rounded-2xl bg-slate-100 p-5">
            <div className="h-5 w-3/4 animate-pulse rounded bg-slate-200 mb-3" />
            <div className="h-4 w-1/2 animate-pulse rounded bg-slate-200 mb-2" />
            <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
          </div>
        ))}
      </div>
    );
  }

  if (!data) return null;

  const isFallback = data.overall_summary?.toLowerCase().includes('fallback') ?? false;

  return (
    <div className="space-y-5">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-800">
          Top {data.recommendations.length} Recommendations
        </h2>
        {isFallback && (
          <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">
            Fallback Mode
          </span>
        )}
      </div>

      {data.recommendations.length === 0 && (
        <div className="rounded-2xl bg-slate-50 p-6 text-center text-slate-500 text-sm">
          No restaurants match your criteria. Try adjusting your filters.
        </div>
      )}

      {data.recommendations.map((rec) => (
        <div
          key={rec.restaurant.id}
          className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm hover:shadow-md transition"
        >
          {/* Title row */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2.5 min-w-0">
              <span className="flex-shrink-0 flex h-7 w-7 items-center justify-center rounded-full bg-rose-500 text-xs font-bold text-white">
                {rec.rank}
              </span>
              <h3 className="text-base font-semibold text-slate-800 truncate">{rec.restaurant.name}</h3>
            </div>
            <div className="flex-shrink-0 text-right">
              <div className="text-lg font-bold text-slate-800 leading-none">
                {rec.restaurant.rating.toFixed(1)}
              </div>
              <StarRating rating={rec.restaurant.rating} />
            </div>
          </div>

          {/* Location */}
          <p className="mt-1 text-xs text-slate-400">{rec.restaurant.location}</p>

          {/* Cuisine chips */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {rec.restaurant.cuisines.slice(0, 5).map((c) => (
              <span
                key={c}
                className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600"
              >
                {c}
              </span>
            ))}
          </div>

          {/* Cost */}
          {rec.restaurant.cost_for_two != null && (
            <p className="mt-2 text-sm font-medium text-slate-600">
              Cost for two:{' '}
              <span className="text-rose-600 font-semibold">
                Rs.{rec.restaurant.cost_for_two.toLocaleString()}
              </span>
            </p>
          )}

          {/* Explanation */}
          <p className="mt-3 text-sm leading-relaxed text-slate-500 bg-slate-50 rounded-xl px-3 py-2.5">
            {rec.explanation}
          </p>
        </div>
      ))}

      {/* Summary */}
      {data.overall_summary && (
        <div className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-800 font-medium">
          {data.overall_summary}
        </div>
      )}
    </div>
  );
}
