import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL!;

export type MeResponse =
  | { authenticated: false }
  | {
      authenticated: true;
      user: { email: string; name: string; picture: string; sub: string };
      google_connected: boolean;
    };


export type SessionResponse = {
  status: string;
  user: MeResponse;
};


export async function getMe(): Promise<MeResponse> {
  console.log("All cookies:", document.cookie);
  
  // Check if jwt_session cookie exists
  const hasJwtCookie = document.cookie.includes('jwt_session=');
  console.log("Has jwt_session cookie:", hasJwtCookie);
  
  try {
    // First try with cookies
    let res = await fetch(`${API}/auth/me`, {
      credentials: "include",
      cache: "no-store",
      headers: {
        "cache-control": "no-cache",
        pragma: "no-cache",
      },
    });
    
    // If cookie auth fails, try with localStorage token
    if (!res.ok && !hasJwtCookie) {
      const storedToken = localStorage.getItem('jwt_token');
      if (storedToken) {
        console.log('Cookie auth failed, trying with stored token');
        res = await fetch(`${API}/auth/me`, {
          credentials: "include",
          cache: "no-store",
          headers: {
            "cache-control": "no-cache",
            pragma: "no-cache",
            "Authorization": `Bearer ${storedToken}`,
          },
        });
      }
    }
    
    if (!res.ok) {
      console.error('Auth check failed:', res.status, res.statusText);
      // Clear stored token if auth fails
      localStorage.removeItem('jwt_token');
      return { authenticated: false };
    }
    
    const result = await res.json();
    console.log('Auth check result:', result);
    return result;
  } catch (error) {
    console.error('Auth request failed:', error);
    return { authenticated: false };
  }
}

export function loginWithGoogle() {
  window.location.href = `${API}/auth/google/login`;
}

export async function logout() {
  await fetch(`${API}/auth/logout`, { 
    method: "POST", 
    credentials: "include" 
  });
  window.location.reload();
}

// Additional helper for checking auth status
export async function checkAuth(): Promise<boolean> {
  try {
    const result = await getMe();
    return result.authenticated;
  } catch (error) {
    console.error('Auth check failed:', error);
    return false;
  }
}

export async function createSessionFromToken(token: string): Promise<MeResponse> {
  try {
    console.log('Creating session with token...');
    const response = await fetch(`${API}/auth/session`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });

    if (response.ok) {
      const data: SessionResponse = await response.json();
      console.log('Session created successfully', data.user);
      
      // Check if cookie was set
      console.log('Cookies after session creation:', document.cookie);
      
      // Wait longer for cookie to be set
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Verify cookie is now present
      const hasJwtCookie = document.cookie.includes('jwt_session=');
      console.log('JWT cookie present after session creation:', hasJwtCookie);
      
      return data.user;
    } else {
      const errorText = await response.text();
      console.error('Failed to create session:', response.status, errorText);
      return { authenticated: false };
    }
  } catch (error) {
    console.error('Error creating session:', error);
    return { authenticated: false };
  }
}

// Hook for React components
export function useAuth() {
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const authStatus = await getMe();
      console.log("authStatus: ", authStatus);
      setUser(authStatus);
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser({ authenticated: false });
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    loginWithGoogle,
    logout,
    checkAuthStatus
  };
}