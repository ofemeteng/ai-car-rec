// LensToast.tsx
"use client";

import * as Toast from "@radix-ui/react-toast";
import { useState, useEffect } from "react";

export function LensToast({ txHash }: { txHash: string }) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (txHash) {
      setOpen(true);
      const timer = setTimeout(() => setOpen(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [txHash]);

  return (
    <Toast.Provider swipeDirection="right">
      <Toast.Root
        open={open}
        onOpenChange={setOpen}
        className="bg-white border border-gray-200 shadow-md rounded-md px-4 py-3 text-sm space-y-2"
      >
        <Toast.Title className="font-semibold text-green-600">
          ✅ Saved to Lens!
        </Toast.Title>
        <Toast.Description>
          <a
            href={`https://explorer.lens.xyz/tx/${txHash}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            View Transaction
          </a>
        </Toast.Description>
      </Toast.Root>
      <Toast.Viewport className="fixed bottom-4 right-4 w-96 max-w-full z-50" />
    </Toast.Provider>
  );
}
