// components/emails/EmailList.tsx
"use client";
import React from "react";
import EmailCard from "./EmailCard";

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

interface EmailListProps {
  emails: Email[];
  selectedEmails: Set<string>;
  onEmailSelect: (emailId: string) => void;
  onEmailClick: (email: Email) => void;
}

export default function EmailList({ 
  emails, 
  selectedEmails, 
  onEmailSelect, 
  onEmailClick 
}: EmailListProps) {
  if (emails.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-8 text-center">
        <div className="text-gray-400 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No emails yet</h3>
        <p className="text-gray-500">
          Emails sorted into this category will appear here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {emails.map((email) => (
        <EmailCard
          key={email.id}
          email={email}
          isSelected={selectedEmails.has(email.id)}
          onSelect={() => onEmailSelect(email.id)}
          onClick={() => onEmailClick(email)}
        />
      ))}
    </div>
  );
}