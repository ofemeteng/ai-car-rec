import { getLensClient } from "@/lib/lens/client";
import { fetchAccount } from "@lens-protocol/client/actions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ClientLanding } from "@/components/ClientLanding";

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
  return <ClientLanding account={account} />;
}

