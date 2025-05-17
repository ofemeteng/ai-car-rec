import type { Metadata } from "next";
import localFont from "next/font/local";
import "@copilotkit/react-ui/styles.css";
import "./globals.css";
import { ModelSelectorProvider } from "@/lib/model-selector-provider";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "AI Car Recommendations",
  description: "Get AI Generated Car Recommendations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ModelSelectorProvider>{children}</ModelSelectorProvider>
      </body>
    </html>
  );
}
