// src/components/Header.tsx
"use client";
import React, { useEffect, useState } from "react";
import { getMe, loginWithGoogle, logout, type MeResponse } from "@/lib/auth";
import Image from "next/image";

const API = process.env.NEXT_PUBLIC_API_URL!;

export default function Header() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((data) => {
        setMe(data);
      })
      .catch(() => setMe({ authenticated: false }))
      .finally(() => setLoading(false));
  }, []);

  // Show minimal loading state that matches server render
  if (me === null) {
    return (
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
        <div className="font-semibold text-lg">AI Email Sorter</div>
        <div className="flex items-center gap-3">
          {/* Simple loading state that matches server render */}
          <div className="w-24 h-8 bg-gray-200 rounded"></div>
          <div className="w-8 h-8 rounded-full bg-gray-200"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-white">
      <div className="font-semibold text-lg">AI Email Sorter</div>
      <div className="flex items-center gap-3">
        {me.authenticated ? (
          <div className="flex items-center gap-4">

            {/* User Profile with Picture */}
            <div className="flex items-center gap-2">
              {me.user.picture && (
                <Image 
                  src={me.user.picture} 
                  alt={me.user.name}
                  width={32}
                  height={32}
                  className="rounded-full"
                />
              )}
              <div className="flex flex-col text-right">
                <span className="text-sm font-medium text-gray-900">
                  {me.user.name}
                </span>
                <span className="text-xs text-gray-500">
                  {me.user.email}
                </span>
              </div>
            </div>
            <button 
              onClick={logout} 
              className="text-sm rounded-full border border-gray-300 px-4 py-2 hover:bg-gray-50 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <button 
            onClick={loginWithGoogle} 
            className="text-sm rounded-full bg-blue-500 text-white px-4 py-2 hover:bg-blue-600 transition-colors"
          >
            Sign in with Google
          </button>
        )}
      </div>
    </div>
  );
}