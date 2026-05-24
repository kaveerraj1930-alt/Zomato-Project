'use client';

import { useState } from 'react';
import PreferenceForm, { FormData } from './components/PreferenceForm';
import ResultsPanel from './components/ResultsPanel';
import { getRecommendations, SummaryData } from '@/lib/api';

export default function Home() {
  const [results, setResults] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    try {
      const summary = await getRecommendations({
        location: data.location,
        budget: data.budget,
        cuisine: data.cuisine,
        min_rating: data.min_rating,
      });
      setResults(summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen">
      {/* Food photo background overlay */}
      <div
        className="fixed inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1920&q=80')",
        }}
      />
      {/* Dark overlay */}
      <div className="fixed inset-0 bg-black/60" />

      {/* Content */}
      <div className="relative z-10 flex min-h-screen flex-col">
        {/* Top nav */}
        <nav className="flex items-center gap-3 px-8 py-4 bg-white/95 shadow-sm">
          <span className="text-xl font-bold text-rose-600 tracking-tight">zomato</span>
          <span className="text-slate-300 text-lg font-light">|</span>
          <span className="text-sm font-medium text-slate-700">AI Recommendation</span>
        </nav>

        {/* Main content */}
        <div className="flex flex-1 flex-col items-center px-4 py-10 gap-8">
          {/* Error banner */}
          {error && (
            <div className="w-full max-w-2xl rounded-xl bg-red-50 p-4 text-sm font-medium text-red-700 shadow">
              {error}
            </div>
          )}

          {/* Form card */}
          <div className="w-full max-w-2xl rounded-2xl bg-white/95 backdrop-blur-sm shadow-2xl p-8">
            <PreferenceForm onSubmit={handleSubmit} loading={loading} />
          </div>

          {/* Results card — shown after submit */}
          {(results || loading) && (
            <div className="w-full max-w-2xl rounded-2xl bg-white/95 backdrop-blur-sm shadow-2xl p-8">
              <ResultsPanel data={results} loading={loading} />
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="relative z-10 py-4 text-center text-xs text-white/50">
          Built with FastAPI + Next.js + Groq LLM
        </footer>
      </div>
    </div>
  );
}
