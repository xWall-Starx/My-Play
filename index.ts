import { createClient } from "jsr:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (request: Request) => {
  if (request.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const authorization = request.headers.get("Authorization");
    if (!authorization?.startsWith("Bearer ")) {
      return jsonResponse({ error: "Authentication required." }, 401);
    }

    const body = await request.json().catch(() => ({}));
    if (body.confirm !== "DELETE MY ACCOUNT") {
      return jsonResponse({ error: "Deletion confirmation did not match." }, 400);
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const anonKey = Deno.env.get("SUPABASE_ANON_KEY");
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !anonKey || !serviceRoleKey) {
      return jsonResponse({ error: "Server deletion service is not configured." }, 500);
    }

    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: authorization } },
      auth: { persistSession: false },
    });
    const token = authorization.replace("Bearer ", "");
    const { data: userData, error: userError } = await userClient.auth.getUser(token);
    if (userError || !userData.user) {
      return jsonResponse({ error: "Your session is no longer valid." }, 401);
    }

    const userId = userData.user.id;
    const admin = createClient(supabaseUrl, serviceRoleKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    // Remove private swing-video objects before deleting their metadata.
    const { data: storedFiles, error: listError } = await admin.storage
      .from("Swing-Videos")
      .list(userId, { limit: 1000 });
    if (listError && !String(listError.message).toLowerCase().includes("not found")) {
      throw listError;
    }
    const objectPaths = (storedFiles ?? [])
      .filter((item) => item.name)
      .map((item) => `${userId}/${item.name}`);
    if (objectPaths.length > 0) {
      const { error: storageError } = await admin.storage
        .from("Swing-Videos")
        .remove(objectPaths);
      if (storageError) throw storageError;
    }

    // Child records come first so deletion works even without cascade rules.
    const tables = [
      "round_holes",
      "swing_videos",
      "data_imports",
      "player_evidence",
      "swing_reminders",
      "golf_bag",
      "player_game_profiles",
      "rounds",
      "profiles",
    ];
    for (const table of tables) {
      const { error } = await admin.from(table).delete().eq("user_id", userId);
      if (error) throw error;
    }

    const { error: deleteUserError } = await admin.auth.admin.deleteUser(userId);
    if (deleteUserError) throw deleteUserError;

    return jsonResponse({ deleted: true }, 200);
  } catch (error) {
    console.error("delete-my-account failed", error);
    return jsonResponse(
      { error: error instanceof Error ? error.message : "Account deletion failed." },
      500,
    );
  }
});

function jsonResponse(body: Record<string, unknown>, status: number) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}
