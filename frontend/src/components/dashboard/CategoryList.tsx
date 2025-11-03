// components/dashboard/CategoryList.tsx
"use client";
import React from "react";

export type Category = {
  id: string;
  name: string;
  description: string;
  email_count: number;
  created_at: string;
};

interface CategoryListProps {
  categories: Category[];
  onAddCategory: () => void;
  onCategoryClick: (category: Category) => void;
  onDeleteCategory?: (categoryId: string) => void;
}

export default function CategoryList({ 
  categories, 
  onAddCategory, 
  onCategoryClick,
  onDeleteCategory 
}: CategoryListProps) {
  
  const handleDeleteClick = (e: React.MouseEvent, categoryId: string) => {
    e.stopPropagation(); // Prevent triggering onCategoryClick
    if (onDeleteCategory && confirm('Are you sure you want to delete this category? Emails in this category will be moved to uncategorized.')) {
      onDeleteCategory(categoryId);
    }
  };
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Your Categories</h2>
        <button
          onClick={onAddCategory}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors font-medium"
        >
          Add Category
        </button>
      </div>

      {categories.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No categories yet</h3>
          <p className="text-gray-500">
            Create your first category to start organizing emails with AI
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {categories.map((category) => (
            <div
              key={category.id}
              onClick={() => onCategoryClick(category)}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-gray-900 text-lg group-hover:text-blue-600">
                  {category.name}
                </h3>
                <div className="flex items-center gap-2">
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    {category.email_count} emails
                  </span>
                  {onDeleteCategory && (
                    <button
                      onClick={(e) => handleDeleteClick(e, category.id)}
                      className="text-gray-400 hover:text-red-500 transition-colors p-1"
                      title="Delete category"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{category.description}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>Created {new Date(category.created_at).toLocaleDateString()}</span>
                <span className="text-blue-500 group-hover:text-blue-700 font-medium">
                  View emails →
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}