"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { CopilotKit } from "@copilotkit/react-core";
import { useModelSelectorContext } from "@/lib/model-selector-provider";
import Main from "./../app/Main";

export default function ClientHome({ account }: { account: any }) {
  const { agent, lgcDeploymentUrl } = useModelSelectorContext();

  const runtimeUrl = lgcDeploymentUrl
    ? `/api/copilotkit?lgcDeploymentUrl=${lgcDeploymentUrl}`
    : `/api/copilotkit${
        agent.includes("crewai") ? "?coAgentsModel=crewai" : ""
      }`;

  return (
    <CopilotKit runtimeUrl={runtimeUrl} showDevConsole={false} agent={agent}>
      <div className="flex h-[60px] bg-[#0E103D] text-white items-center justify-between px-10">
        <h1 className="text-2xl font-medium">AI Car Recommendation</h1>

        <div className="flex items-center gap-3">
            <Avatar className="h-8 w-8">
              <AvatarImage src={account.metadata?.picture} />
              <AvatarFallback>
                {account.address?.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col text-xs leading-tight text-white">
              <span className="font-medium">{account.metadata?.name ?? "Unnamed"}</span>
              <span className="opacity-70 truncate w-[100px]">{account.address}</span>
            </div>
          </div>
      </div>
      {/* <div className="flex flex-col items-center justify-center">
        <Card className="w-full max-w-lg">
          <CardHeader className="flex flex-row items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarImage src={account.metadata?.picture} />
              <AvatarFallback>{account.address.substring(0, 2).toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-xl">{account.metadata?.name}</CardTitle>
              <CardDescription className="mt-1">
                {account.address}
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Successfully authenticated with Lens Protocol
            </p>
          </CardContent>
        </Card>
      </div> */}
      <Main />
    </CopilotKit>
  );
}
