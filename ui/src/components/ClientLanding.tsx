"use client";

import { Login } from "@/components/login";
import ClientHome from "@/components/ClientHome";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export function ClientLanding({ account }: { account: any }) {
  if (account) {
    return <ClientHome account={account} />;
  }

  return (
    <main className="min-h-screen w-full bg-[#E0E9FD] flex items-center justify-center px-4">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-lg p-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-[#6766FC]">🚘 DriveLens - AI Car Recommendations</h1>
          <p className="mt-2 text-gray-700 text-lg">
            Your expert AI car research assistant on Lens Protocol.
          </p>
        </header>

        <section className="grid gap-6 sm:grid-cols-2 text-sm text-gray-800">
          <div className="bg-[#F3F4F6] rounded-xl p-4 shadow-inner">
            🚘 Ask in natural language for the best car recommendations tailored to your needs.
          </div>
          <div className="bg-[#F3F4F6] rounded-xl p-4 shadow-inner">
            🧠 AI-generated car suggestions curated by preferences and needs.
          </div>
          <div className="bg-[#F3F4F6] rounded-xl p-4 shadow-inner">
            💾 Save your top picks to the global Lens feed and access them anytime.
          </div>
          <div className="bg-[#F3F4F6] rounded-xl p-4 shadow-inner">
            🔐 Log in with Lens, ConnectKit and Continue with Family. Your wallet is your identity.
          </div>
        </section>

        <div className="mt-10 flex justify-center">
          <Login />
        </div>
      </div>
    </main>
  );
}
