// components/dashboard/ConnectedAccounts.tsx
"use client";
import React from "react";
import Image from "next/image";
import type { ConnectedAccount as ConnectedAccountType } from "@/app/dashboard/page";
import Link from "next/link";
import { loginWithGoogle } from "@/lib/auth";

export default function ConnectedAccounts({ accounts, onConnectNewAccount }: { accounts: ConnectedAccountType[]; onConnectNewAccount?: () => void | Promise<void> }) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 h-full">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Connected Gmail Accounts</h2>
      
      <div className="space-y-3 mb-6">
        {accounts.map((account) => (
          <div key={account.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              {account.picture && (
                  <Image 
                    src={account.picture} 
                    alt={account.email}
                    width={32}
                    height={32}
                    className="rounded-full"
                  />
              )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">{account.email}</p>
                <p className="text-xs text-gray-500">
                  Connected {new Date(account.connected_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            {account.is_primary && (
              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                Primary
              </span>
            )}
          </div>
        ))}
        
        {accounts.length === 0 && (
          <div className="text-center py-4">
            <p className="text-gray-500 text-sm">No Gmail accounts connected yet</p>
          </div>
        )}
      </div>

      <div className="flex justify-end">
          <button className="w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 transition-colors font-medium" onClick={onConnectNewAccount ?? loginWithGoogle} >
            Add New Account
          </button>
      </div>
    </div>
  );
}     