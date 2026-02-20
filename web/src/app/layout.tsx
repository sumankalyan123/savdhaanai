import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/navbar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Savdhaan AI — Is this a scam?",
  description:
    "Paste any suspicious message and get an instant, evidence-based risk assessment. Free scam detection for SMS, email, WhatsApp, and more.",
  openGraph: {
    title: "Savdhaan AI — Is this a scam?",
    description: "AI-powered scam detection. Paste a message, get the truth.",
    siteName: "Savdhaan AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-gray-50`}>
        <Navbar />
        {children}
      </body>
    </html>
  );
}
