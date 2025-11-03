// app/auth-callback/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { createSessionFromToken } from '@/lib/auth';

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const processAuthCallback = async () => {
      // Get token from URL parameters
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');

      console.log('Auth callback received, processing token...', token ? 'Token present' : 'No token');

      if (token) {
        try {
          // Decode the URL-encoded token
          const decodedToken = decodeURIComponent(token);
          console.log('Decoded token length:', decodedToken.length);
          
          // Create session and get user details
          const userData = await createSessionFromToken(decodedToken);
          
          if (userData.authenticated) {
            console.log('Authentication successful:', userData.user.email);
            
            // Clear the URL parameters
            window.history.replaceState({}, document.title, '/auth-callback');
            
            // Wait a bit more for cookie to be fully set
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Force a hard redirect to ensure cookies are properly set
            window.location.href = '/dashboard';
          } else {
            console.error('Authentication failed - user data not authenticated');
            router.push('/?error=auth_failed');
          }
        } catch (error) {
          console.error('Error during authentication:', error);
          router.push('/?error=network_error');
        }
      } else {
        console.error('No token found in URL');
        router.push('/?error=no_token');
      }
    };

    processAuthCallback();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Completing Sign In...</h1>
        <p className="text-gray-600 mb-4">Setting up your account and preferences. Please wait...</p>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
      </div>
    </div>
  );
}
