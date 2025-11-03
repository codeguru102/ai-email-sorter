// components/emails/BulkActions.tsx
"use client";
import React from "react";

interface BulkActionsProps {
  selectedCount: number;
  totalCount: number;
  onSelectAll: () => void;
  onDelete: () => void;
  onUnsubscribe: () => void;
  onClearSelection: () => void;
}

export default function BulkActions({
  selectedCount,
  totalCount,
  onSelectAll,
  onDelete,
  onUnsubscribe,
  onClearSelection,
}: BulkActionsProps) {
  const allSelected = selectedCount === totalCount;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <span className="text-blue-800 font-medium">
            {selectedCount} {selectedCount === 1 ? 'email' : 'emails'} selected
          </span>
          
          <button
            onClick={onSelectAll}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            {allSelected ? 'Deselect all' : `Select all ${totalCount} emails`}
          </button>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onUnsubscribe}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
          >
            Unsubscribe ({selectedCount})
          </button>
          
          <button
            onClick={onDelete}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
          >
            Delete ({selectedCount})
          </button>
          
          <button
            onClick={onClearSelection}
            className="text-gray-500 hover:text-gray-700 text-sm font-medium"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  );
}