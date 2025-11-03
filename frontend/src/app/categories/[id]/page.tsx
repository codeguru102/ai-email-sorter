// app/categories/[id]/page.tsx
"use client";
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import EmailList from "@/components/emails/EmailList";
import BulkActions from "@/components/emails/BulkActions";
import { getMe, type MeResponse } from "@/lib/auth";

export type Email = {
  id: string;
  subject: string;
  from: string;
  from_email: string;
  summary: string;
  received_at: string;
  category_id: string;
  read: boolean;
  body_preview: string;
};

export default function CategoryPage() {
  const params = useParams();
  const router = useRouter();
  const categoryId = params.id as string;
  
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmails, setSelectedEmails] = useState<Set<string>>(new Set());
  const [category, setCategory] = useState({ name: "Loading..." });

  useEffect(() => {
    getMe()
      .then(setMe)
      .catch(() => setMe({ authenticated: false }))
      .finally(() => setLoading(false));

    fetchCategoryEmails();
  }, [categoryId]);

  const fetchCategoryEmails = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/emails/category/${categoryId}`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const emailsData = await response.json();
        const formattedEmails: Email[] = emailsData.map((email: any) => ({
          id: email.id.toString(),
          subject: email.subject,
          from: email.sender,
          from_email: email.sender_email,
          summary: email.body_preview,
          received_at: email.received_at,
          category_id: categoryId,
          read: email.is_read,
          body_preview: email.body_preview
        }));
        
        setEmails(formattedEmails);
        
        // Fetch category info
        const categoriesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/emails/categories`, {
          credentials: 'include',
        });
        
        if (categoriesResponse.ok) {
          const categories = await categoriesResponse.json();
          const currentCategory = categories.find((cat: any) => cat.id.toString() === categoryId);
          if (currentCategory) {
            setCategory({ name: currentCategory.name });
          }
        }
      } else {
        console.error('Failed to fetch emails:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch category emails:', error);
    }
  };

  const toggleEmailSelection = (emailId: string) => {
    const newSelected = new Set(selectedEmails);
    if (newSelected.has(emailId)) {
      newSelected.delete(emailId);
    } else {
      newSelected.add(emailId);
    }
    setSelectedEmails(newSelected);
  };

  const selectAllEmails = () => {
    if (selectedEmails.size === emails.length) {
      setSelectedEmails(new Set());
    } else {
      setSelectedEmails(new Set(emails.map(email => email.id)));
    }
  };

  const handleBulkDelete = async () => {
    // Implement bulk delete logic
    console.log('Deleting emails:', Array.from(selectedEmails));
    setSelectedEmails(new Set());
  };

  const handleBulkUnsubscribe = async () => {
    // Implement bulk unsubscribe logic
    console.log('Unsubscribing from emails:', Array.from(selectedEmails));
    setSelectedEmails(new Set());
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-sm text-gray-600">Loading category...</div>
          </div>
        </div>
      </main>
    );
  }

  if (!me?.authenticated) {
    router.push('/dashboard');
    return null;
  }

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="flex items-center text-blue-500 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{category.name}</h1>
          <p className="text-gray-600 mt-2">
            {emails.length} emails in this category
          </p>
        </div>

        {/* Bulk Actions */}
        {selectedEmails.size > 0 && (
          <BulkActions
            selectedCount={selectedEmails.size}
            totalCount={emails.length}
            onSelectAll={selectAllEmails}
            onDelete={handleBulkDelete}
            onUnsubscribe={handleBulkUnsubscribe}
            onClearSelection={() => setSelectedEmails(new Set())}
          />
        )}

        {/* Email List */}
        <EmailList
          emails={emails}
          selectedEmails={selectedEmails}
          onEmailSelect={toggleEmailSelection}
          onEmailClick={(email: Email) => {
            // Navigate to email detail or show modal
            console.log('View email:', email.id);
          }}
        />
      </div>
    </main>
  );
}