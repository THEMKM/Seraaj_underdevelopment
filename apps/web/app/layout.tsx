import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "../contexts/ThemeContext";
import { LanguageProvider } from "../contexts/LanguageContext";
import { WebSocketProvider } from "../contexts/WebSocketContext";
import { AuthProvider } from "../contexts/AuthContext";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Seraaj - Turn Goodwill Into Impact",
  description: "Two-sided volunteer marketplace for MENA nonprofits",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className={`${inter.variable} font-body bg-white dark:bg-dark-bg text-ink dark:text-white min-h-screen transition-colors duration-300`}>
        <LanguageProvider>
          <ThemeProvider>
            <AuthProvider>
              <WebSocketProvider>
                {children}
              </WebSocketProvider>
            </AuthProvider>
          </ThemeProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
