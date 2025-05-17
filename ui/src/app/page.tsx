import { Login } from "@/components/login";
import { getLensClient } from "@/lib/lens/client";
import { fetchAccount } from "@lens-protocol/client/actions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import ClientHome from "@/components/ClientHome";

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

export default async function Home() {
  const account = await getAuthenticatedAccount();

  if (!account) {
    return (
      <div className="flex flex-col items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>AI Car Recommendation</CardTitle>
            <CardDescription>Your expert AI Car Research Assistant.</CardDescription>
          </CardHeader>
          <CardContent>
            <Login />
          </CardContent>
        </Card>
      </div>
    );
  }

  return <ClientHome account={account} />;
}
