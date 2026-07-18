import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "LearnPDF — Turn PDFs into AI Courses",
  description:
    "Upload any PDF and instantly generate a structured course with chapters, lessons, quizzes and an AI tutor that answers from your document.",
  keywords: ["AI", "e-learning", "PDF", "RAG", "courses", "quizzes"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
