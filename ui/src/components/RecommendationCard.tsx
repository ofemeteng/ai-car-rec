import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Recommendation } from "@/lib/types";
import { Info, Save, MoreHorizontal } from "lucide-react";
import { useState } from "react";
import { getLensClient } from "@/lib/lens/client";
import { fetchAccount } from "@lens-protocol/client/actions";
import { textOnly } from "@lens-protocol/metadata";
import { StorageClient } from "@lens-chain/storage-client";
import { uri as lensUri, SessionClient, Context } from "@lens-protocol/client";
import { useWalletClient } from "wagmi";
import { handleOperationWith } from "@lens-protocol/client/viem";
import { post } from "@lens-protocol/client/actions";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LensToast } from "./LensToast";

type RecommendationCardProps = {
  recommendation: Recommendation;
  className?: string;
  number?: number;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
};

/**
 * Fetches authenticated user account if logged in
 */
async function getAuthenticatedAccount() {
  const client = await getLensClient();

  if (!client.isSessionClient()) {
    return null;
  }

  const authenticatedUser = client.getAuthenticatedUser().unwrapOr(null);
  if (!authenticatedUser) {
    return null;
  }

  return fetchAccount(client, { address: authenticatedUser.address }).unwrapOr(null);
}

export function RecommendationCard({
  recommendation,
  onMouseEnter,
  onMouseLeave,
  className,
  number,
}: RecommendationCardProps) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [txHash, setTxHash] = useState("");
  const { data: walletClient } = useWalletClient();
  

  async function handleSave() {
    try {
      setIsSaving(true);
      const account = await getAuthenticatedAccount();

      if (!account) {
        console.error("No authenticated account found");
        return;
      }

      const name = account.metadata?.name ?? null
      const address = account.address ?? null

      const savedBy = name || address

      const content = JSON.stringify({
        car: recommendation.car,
        tagline: recommendation.tagline,
        content: recommendation.content,
        curator: savedBy
      });

      console.log("content: ", String(content));

      const metadata = textOnly({
        content: content,
      });

      const storageClient = StorageClient.create();
      const { uri } = await storageClient.uploadAsJson(metadata);

      const client = await getLensClient();

      const sessionClient = client as SessionClient<Context>;

      const result = await post(sessionClient, {
        contentUri: lensUri(uri),
      }).andThen(handleOperationWith(walletClient));

      console.log("result: ", result);

      if (result) {
        result.map((txHash) => {
          console.log("txHash: ", txHash);
          setTxHash(txHash);
        });
      }

    } catch (err: any) {
      console.error(err);
      alert(`❌ Error saving to Lens:\n${err.message}`);
    } finally {
      setIsSaving(false);
    }
    
  };

  return (
    <Card
      className={cn(
        "bg-background rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 ease-in-out",
        className
      )}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      <CardContent className="p-6">
        <div className="flex flex-col space-y-4">
          <div className="flex justify-between items-start gap-4">
            <div className="flex-grow space-y-1.5">
              <CardTitle className="text-lg md:text-xl font-bold flex items-center gap-3">
                {number && (
                  <div className="flex-shrink-0 text-xs bg-primary text-primary-foreground rounded-full flex items-center justify-center font-semibold w-8 h-8 border-2 border-background ring-1 ring-primary/50">
                    {number}
                  </div>
                )}
                <span className="leading-tight">{recommendation.car}</span>
              </CardTitle>
            </div>
            <div className="flex-shrink-0">
              <DropdownMenu open={dropdownOpen} onOpenChange={setDropdownOpen}>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={handleSave}
                    disabled={isSaving}
                    className={cn("text-primary", isSaving && "opacity-50 pointer-events-none")}
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {isSaving ? "Saving..." : "Save to Lens"}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          <LensToast txHash={txHash} />
          <div className="space-y-3 text-sm">
            {recommendation.tagline && (
              <p className="italic text-muted-foreground">
                "{recommendation.tagline}"
              </p>
            )}
            {recommendation.content && (
              <div className="flex items-start gap-2 pt-1 text-foreground/80">
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-primary" />
                <p className="flex-1">{recommendation.content}</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
