'use client';

import { useState, useEffect, FormEvent } from 'react';
import { getLocations, getCuisines } from '@/lib/api';

export interface FormData {
  location: string;
  budget: 'low' | 'medium' | 'high';
  cuisine: string;
  min_rating: number;
  cravings?: string;
  additional?: string;
}

interface PreferenceFormProps {
  onSubmit: (data: FormData) => void;
  loading: boolean;
}

/** Convert a numeric budget (cost for two) into the band the backend expects. */
function amountToBand(amount: number): 'low' | 'medium' | 'high' {
  if (amount <= 500) return 'low';
  if (amount <= 1000) return 'medium';
  return 'high';
}

const QUICK_CHIPS = ['Italian', 'Spicy', 'Dessert', 'Chinese', 'Biryani', 'Healthy'];

const RATING_OPTIONS = [
  { label: 'Any rating', value: 0 },
  { label: '3.0+ stars', value: 3.0 },
  { label: '3.5+ stars', value: 3.5 },
  { label: '4.0+ stars', value: 4.0 },
  { label: '4.5+ stars', value: 4.5 },
];

const MAX_ADDITIONAL = 4000;

export default function PreferenceForm({ onSubmit, loading }: PreferenceFormProps) {
  const [location, setLocation] = useState('');
  const [budgetRaw, setBudgetRaw] = useState('2000');
  const [cuisine, setCuisine] = useState('');
  const [minRating, setMinRating] = useState(3.5);
  const [cravings, setCravings] = useState('');
  const [additional, setAdditional] = useState('');
  const [locations, setLocations] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);

  useEffect(() => {
    getLocations().then(setLocations).catch(() => setLocations([]));
    getCuisines().then(setCuisines).catch(() => setCuisines([]));
  }, []);

  const budgetAmount = parseInt(budgetRaw) || 0;
  const budgetBand = amountToBand(budgetAmount);

  const handleChip = (chip: string) => {
    setCuisine((prev) => {
      const parts = prev.split(',').map((s) => s.trim()).filter(Boolean);
      if (parts.includes(chip)) return parts.filter((p) => p !== chip).join(', ');
      return [...parts, chip].join(', ');
    });
  };

  const activeChips = cuisine.split(',').map((s) => s.trim()).filter(Boolean);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({
      location,
      budget: budgetBand,
      cuisine,
      min_rating: minRating,
      cravings,
      additional,
    });
  };

  const inputCls =
    'w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent transition';

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-slate-900">
          Find Your Perfect Meal with Zomato AI
        </h1>
      </div>

      {/* Quick cuisine chips */}
      <div className="flex flex-wrap justify-center gap-2">
        {QUICK_CHIPS.map((chip) => (
          <button
            key={chip}
            type="button"
            onClick={() => handleChip(chip)}
            className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${
              activeChips.includes(chip)
                ? 'border-rose-500 bg-rose-50 text-rose-700'
                : 'border-slate-300 bg-white text-slate-600 hover:border-rose-400 hover:text-rose-600'
            }`}
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Row 1: Location + Cuisine */}
      <div className="grid grid-cols-2 gap-4">
        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Location</label>
          <div className="relative">
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className={`${inputCls} appearance-none pr-10`}
              required
            >
              <option value="" disabled>Select location...</option>
              {locations.map((loc) => (
                <option key={loc} value={loc}>{loc}</option>
              ))}
            </select>
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">▾</span>
          </div>
        </div>

        {/* Cuisine */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Cuisine</label>
          <input
            list="cuisine-list"
            type="text"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
            className={inputCls}
            placeholder="e.g. North Indian"
          />
          <datalist id="cuisine-list">
            {cuisines.map((c) => (
              <option key={c} value={c} />
            ))}
          </datalist>
        </div>
      </div>

      {/* Row 2: Budget + Rating */}
      <div className="grid grid-cols-2 gap-4">
        {/* Budget */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">Budget</label>
          <input
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            value={budgetRaw}
            onChange={(e) => {
              const raw = e.target.value.replace(/[^0-9]/g, '');
              setBudgetRaw(raw === '' ? '' : String(parseInt(raw, 10)));
            }}
            className={inputCls}
            placeholder="e.g. 2000"
            required
          />
          {budgetRaw !== '' && (
            <p className="mt-1 text-xs text-slate-400">
              Band:{' '}
              <span
                className={
                  budgetBand === 'low'
                    ? 'font-semibold text-green-600'
                    : budgetBand === 'medium'
                    ? 'font-semibold text-amber-600'
                    : 'font-semibold text-rose-600'
                }
              >
                {budgetBand.charAt(0).toUpperCase() + budgetBand.slice(1)}
              </span>
            </p>
          )}
        </div>

        {/* Min Rating */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            <span className="text-amber-400 mr-1">★</span>Minimum rating
          </label>
          <div className="relative">
            <select
              value={minRating}
              onChange={(e) => setMinRating(parseFloat(e.target.value))}
              className={`${inputCls} appearance-none pr-10`}
            >
              {RATING_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs">▾</span>
          </div>
        </div>
      </div>

      {/* Specific Cravings */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-1.5">Specific Cravings</label>
        <input
          type="text"
          value={cravings}
          onChange={(e) => setCravings(e.target.value)}
          className={inputCls}
          placeholder="e.g. Spicy"
        />
      </div>

      {/* Additional Preferences */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-0.5">
          Additional preferences
        </label>
        <p className="text-xs text-slate-400 mb-1.5">
          Dietary needs, vibe, occasion, dishes to avoid—anything that helps narrow picks.
          Combined with cravings and budget notes: up to {MAX_ADDITIONAL.toLocaleString()} characters.
        </p>
        <div className="relative">
          <textarea
            value={additional}
            onChange={(e) => setAdditional(e.target.value.slice(0, MAX_ADDITIONAL))}
            rows={4}
            className={`${inputCls} resize-none`}
            placeholder="e.g., vegetarian only, quiet place for a date, no peanuts..."
          />
          <span className="absolute bottom-2 right-3 text-xs text-slate-400 select-none">
            {additional.length} / {MAX_ADDITIONAL.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-rose-500 px-4 py-3.5 text-sm font-semibold text-white shadow-md hover:bg-rose-600 active:bg-rose-700 disabled:opacity-60 disabled:cursor-not-allowed transition"
      >
        {loading ? 'Finding recommendations...' : 'Get Recommendations'}
      </button>
    </form>
  );
}
