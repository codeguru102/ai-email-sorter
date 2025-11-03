// components/emails/EmailCard.tsx
"use client";
import React from "react";
import type { Email } from "./EmailList";

interface EmailCardProps {
  email: Email;
  isSelected: boolean;
  onSelect: () => void;
  onClick: () => void;
}

export default function EmailCard({ email, isSelected, onSelect, onClick }: EmailCardProps) {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div 
      className={`bg-white border rounded-xl p-4 transition-all cursor-pointer group ${
        isSelected 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
      } ${!email.read ? 'border-l-4 border-l-blue-500' : ''}`}
      onClick={(e) => {
        // Prevent selection when clicking the card directly
        if (e.target === e.currentTarget) {
          onClick();
        }
      }}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <div className="flex items-start pt-1">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onSelect}
            onClick={(e) => e.stopPropagation()}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
        </div>

        {/* Sender Avatar */}
        <div className="flex-shrink-0">
          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">
              {email.from[0].toUpperCase()}
            </span>
          </div>
        </div>

        {/* Email Content */}
        <div className="flex-1 min-w-0" onClick={onClick}>
          <div className="flex items-start justify-between mb-1">
            <div className="flex items-center space-x-2">
              <span className={`font-medium ${!email.read ? 'text-gray-900' : 'text-gray-700'}`}>
                {email.from}
              </span>
              <span className="text-gray-500 text-sm">{email.from_email}</span>
            </div>
            <span className="text-gray-400 text-sm flex-shrink-0">
              {formatTime(email.received_at)}
            </span>
          </div>

          <h3 className={`font-semibold mb-1 truncate ${!email.read ? 'text-gray-900' : 'text-gray-700'}`}>
            {email.subject}
          </h3>

          <p className="text-gray-600 text-sm mb-2 line-clamp-2">
            {email.summary}
          </p>

          <p className="text-gray-500 text-xs line-clamp-1">
            {email.body_preview}
          </p>
        </div>
      </div>
    </div>
  );
}