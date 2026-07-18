import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Litmus — Ship AI you can trust",
  description:
    "Open-source platform to evaluate, red-team, and monitor AI systems (LLM · RAG · agents · vision) before and after production.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans">{children}</body>
    </html>
  );
}
