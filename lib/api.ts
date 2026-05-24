// Typed API client for the Zomato Recommendation Backend.
// Calls the backend API directly using the BACKEND_URL environment variable.

const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export interface UserPreferencesInput {
  location: string;
  budget: 'low' | 'medium' | 'high';
  cuisine: string[];
  min_rating: number;
  extras?: Record<string, unknown>;
}

export interface RestaurantData {
  name: string;
  location: string;
  cuisines: string[];
  price_range: string;
  address: string;
  rating: number;
  cost_for_two?: number;
}

export interface RecommendationData {
  rank: number;
  restaurant: RestaurantData;
  explanation: string;
}

export interface SummaryData {
  recommendations: RecommendationData[];
  overall_summary: string | null;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export async function getRecommendations(
  preferences: UserPreferencesInput
): Promise<SummaryData> {
  return fetchJson<SummaryData>(`${API_BASE}/recommendations`, {
    method: 'POST',
    body: JSON.stringify(preferences),
  });
}

export async function getMetadata(): Promise<{ locations: string[]; cuisines: string[] }> {
  return fetchJson<{ locations: string[]; cuisines: string[] }>(`${API_BASE}/metadata`);
}

export async function getLocations(): Promise<string[]> {
  const metadata = await getMetadata();
  return metadata.locations;
}

export async function getCuisines(): Promise<string[]> {
  const metadata = await getMetadata();
  return metadata.cuisines;
}
