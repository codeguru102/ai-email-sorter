"use client";
import React, { useState, useEffect } from "react";

export type Email = {
  id: string;
  subject: string;
  sender: string;
  sender_email: string;
  body_preview: string;
  received_at: string;
  is_read: boolean;
};

interface UncategorizedEmailsProps {
  onCategorizeClick: () => void;
}

export default function UncategorizedEmails({ onCategorizeClick }: UncategorizedEmailsProps) {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUncategorizedEmails();
  }, []);

  const fetchUncategorizedEmails = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;
      const response = await fetch(`${API_URL}/emails/uncategorized`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const emailData = await response.json();
        setEmails(emailData);
      }
    } catch (error) {
      console.error('Failed to fetch uncategorized emails:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-16 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Uncategorized Emails</h2>
          <p className="text-sm text-gray-500">{emails.length} emails need categorization</p>
        </div>
        {emails.length > 0 && (
          <button
            onClick={onCategorizeClick}
            className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors font-medium text-sm"
          >
            AI Categorize
          </button>
        )}
      </div>

      {emails.length === 0 ? (
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">All emails categorized!</h3>
          <p className="text-gray-500">Great job! All your emails have been organized.</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {emails.map((email) => (
            <div
              key={email.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-gray-900 text-sm line-clamp-1">
                  {email.subject || "(No Subject)"}
                </h3>
                <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                  {new Date(email.received_at).toLocaleDateString()}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">From: {email.sender_email}</p>
              <p className="text-xs text-gray-500 line-clamp-2">{email.body_preview}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}