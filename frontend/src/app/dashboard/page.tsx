// src/app/dashboard/page.tsx
"use client";
import React, { useEffect, useState } from "react";
import { getMe, loginWithGoogle, type MeResponse } from "@/lib/auth";
import ConnectedAccounts from "@/components/dashboard/ConnectedAccounts";
import CategoryList from "@/components/dashboard/CategoryList";
import AddCategoryModal from "@/components/dashboard/AddCategoryModal";
import UncategorizedEmails from "@/components/emails/UncategorizedEmails";
import { useRouter } from "next/navigation";

// Types for our email sorting app
export type Category = {
  id: string;
  name: string;
  description: string;
  email_count: number;
  created_at: string;
};

export type ConnectedAccount = {
  id: string;
  email: string;
  picture: string;
  connected_at: string;
  is_primary: boolean;
};

export default function ChatPage() {
  const router = useRouter();
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<ConnectedAccount[]>([]);
  const [showAddCategory, setShowAddCategory] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        console.log('Dashboard: Checking authentication...');
        const data = await getMe();
        console.log('Dashboard: Auth result:', data);
        
        setMe(data);
        
        if (data.authenticated) {
          const loggedInAccount: ConnectedAccount[] = [
            {
              id: "1",
              email: data.user.email,
              picture: data.user.picture || "https://via.placeholder.com/150",
              connected_at: new Date().toISOString(),
              is_primary: true,
            },
          ];
          setAccounts(loggedInAccount);
          
          // Load initial data only if authenticated
          await fetchCategories();
          await fetchConnectedAccounts();
        }
      } catch (error) {
        console.error('Dashboard: Auth check failed:', error);
        setMe({ authenticated: false });
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const fetchCategories = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/categories`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const categories = await response.json();
        setCategories(categories.map((cat: any) => ({
          id: cat.id.toString(),
          name: cat.name,
          description: cat.description,
          email_count: cat.email_count,
          created_at: cat.created_at,
        })));
      } else {
        console.error('Failed to fetch categories:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchConnectedAccounts = async () => {
    try {
      
    } catch (error) {
      console.error('Failed to fetch accounts:', error);
    }
  };

  const handleAddCategory = async (name: string, description: string) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/categories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ name, description }),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`Failed to create category: ${response.status} ${errorText}`);
      }
      
      const newCategory = await response.json();
      
      // Convert the response to match our frontend type
      const categoryForState: Category = {
        id: newCategory.id.toString(),
        name: newCategory.name,
        description: newCategory.description,
        email_count: newCategory.email_count,
        created_at: newCategory.created_at,
      };
      
      setCategories(prev => [...prev, categoryForState]);
      setShowAddCategory(false);
    } catch (error) {
      console.error('Failed to create category:', error);
      throw error; // Re-throw for the modal to handle
    }
  };

  const connectNewAccount = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/add-account`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
        // Refresh categories to show updated counts
        await fetchCategories();
      } else {
        alert('❌ Failed to add account');
      }
    } catch (error) {
      console.error('Failed to connect account:', error);
      alert('❌ Error adding account');
    }
  };

  const handleCategoryClick = (category: Category) => {
    // Navigate to category detail page
    router.push(`/categories/${category.id}`);
  };

  const handleDeleteCategory = async (categoryId: string) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/categories/${categoryId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      
      if (response.ok) {
        const result = await response.json();
        // Remove the category from state
        setCategories(prev => prev.filter(cat => cat.id !== categoryId));
        alert(`✅ ${result.message}`);
      } else {
        const error = await response.text();
        alert(`❌ Failed to delete category: ${error}`);
      }
    } catch (error) {
      console.error('Delete category error:', error);
      alert('❌ Error deleting category');
    }
  };

  const handleEnableNotifications = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/gmail-setup/enable-notifications`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
      } else {
        const error = await response.text();
        alert(`❌ Failed to enable notifications: ${error}`);
      }
    } catch (error) {
      console.error('Enable notifications error:', error);
      alert('❌ Error enabling notifications');
    }
  };

  const handleCategorizeEmails = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/categorize`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
        // Refresh categories to show updated counts
        await fetchCategories();
      } else {
        alert('❌ Failed to categorize emails');
      }
    } catch (error) {
      console.error('Categorization error:', error);
      alert('❌ Error categorizing emails');
    }
  };

  if (loading) {
    return (
      <main className="min-h-[60vh] grid place-items-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <div className="text-sm text-gray-600">Loading your dashboard…</div>
        </div>
      </main>
    );
  }

  if (!me?.authenticated) {
    return (
      <main className="min-h-[60vh] grid place-items-center">
        <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center max-w-md w-full">
          <h1 className="text-2xl font-bold mb-2">Welcome to AI Email Sorter</h1>
          <p className="text-gray-600 mb-6">Please sign in to access your dashboard and start organizing your emails</p>
          <button 
            onClick={() => {
              console.log('Login button clicked');
              loginWithGoogle();
            }} 
            className="w-full rounded-full bg-blue-500 text-white px-6 py-3 hover:bg-blue-600 transition-colors font-medium"
          >
            Sign in with Google
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AI Email Sorting Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Automatically organize your Gmail with AI-powered categorization
          </p>
        </div>
 
        {/* Top Row: Accounts and Categories */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start mb-8">
          
          {/* Section 1: Connected Gmail Accounts */}
          <div className="lg:col-span-1">
            <ConnectedAccounts 
              accounts={accounts}
              onConnectNewAccount={connectNewAccount}
            />
          </div>

          {/* Section 2: Categories List */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Email Categories</h2>
              <div className="flex gap-2">
                <button
                  onClick={handleEnableNotifications}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                >
                  🔔 Enable Auto-Fetch
                </button>
                <button
                  onClick={handleCategorizeEmails}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors text-sm font-medium"
                >
                  🤖 AI Categorize
                </button>
              </div>
            </div>
            <CategoryList 
              categories={categories}
              onAddCategory={() => setShowAddCategory(true)}
              onCategoryClick={handleCategoryClick}
              onDeleteCategory={handleDeleteCategory}
            />
          </div>
        </div>
        
        {/* Bottom Row: Uncategorized Emails */}
        <div className="w-full mt-8">
          <UncategorizedEmails 
            onCategorizeClick={handleCategorizeEmails}
          />
        </div>
      </div>

      {/* Add Category Modal */}
      {showAddCategory && (
        <AddCategoryModal
          onClose={() => setShowAddCategory(false)}
          onSubmit={handleAddCategory}
        />
      )}
    </main>
  );
}