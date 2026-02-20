"use client";

import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-xl font-bold text-gray-900">
          Savdhaan<span className="text-red-600">.ai</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link
            href="/auth"
            className="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            Login
          </Link>
        </div>
      </div>
    </nav>
  );
}
