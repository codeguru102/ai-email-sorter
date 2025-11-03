// lib/api.ts
export const API = process.env.NEXT_PUBLIC_API_URL!;

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API}${endpoint}`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export const emailsAPI = {
  getCategories: () => apiRequest('/emails/categories'),
  getEmails: (categoryId?: number) => 
    apiRequest(`/emails${categoryId ? `?category_id=${categoryId}` : ''}`),
  getEmailsByCategory: (categoryId: number) => 
    apiRequest(`/emails/category/${categoryId}`),
  syncEmails: () => apiRequest('/emails/sync', { method: 'POST' }),
  categorizeEmails: () => apiRequest('/emails/categorize', { method: 'POST' }),
};