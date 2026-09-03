// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "jsr:@supabase/server@1";

export default {
  fetch: withSupabase({ auth: "user" }, async (req, ctx) => {
    try {
      if (req.method !== "POST") {
        return Response.json({ error: "Method not allowed." }, { status: 405 });
      }

      const body = await req.json().catch(() => ({}));
      if (body.confirm !== "DELETE MY ACCOUNT") {
        return Response.json(
          { error: "Deletion confirmation did not match." },
          { status: 400 },
        );
      }

      const userId = ctx.userClaims?.id ?? ctx.jwtClaims?.sub;
      if (!userId) {
        return Response.json({ error: "Authentication required." }, { status: 401 });
      }

      const admin = ctx.supabaseAdmin;

      // Delete private swing-video objects before their database metadata.
      const { data: storedFiles, error: listError } = await admin.storage
        .from("Swing-Videos")
        .list(userId, { limit: 1000 });

      if (
        listError &&
        !String(listError.message).toLowerCase().includes("not found")
      ) {
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

      // Delete private music objects from the golfer's personal folder.
      const { data: musicFiles, error: musicListError } = await admin.storage
        .from("Golf-Music")
        .list(userId, { limit: 1000 });

      if (
        musicListError &&
        !String(musicListError.message).toLowerCase().includes("not found")
      ) {
        throw musicListError;
      }

      const musicPaths = (musicFiles ?? [])
        .filter((item) => item.name)
        .map((item) => `${userId}/${item.name}`);

      if (musicPaths.length > 0) {
        const { error: musicStorageError } = await admin.storage
          .from("Golf-Music")
          .remove(musicPaths);
        if (musicStorageError) throw musicStorageError;
      }

      // Delete child records first so this works without cascade rules.
      const tables = [
        "round_holes",
        "swing_videos",
        "music_tracks",
        "nutrition_logs",
        "performance_checkins",
        "data_imports",
        "player_evidence",
        "swing_reminders",
        "golf_bag",
        "player_game_profiles",
        "rounds",
        "profiles",
      ];

      for (const table of tables) {
        const { error } = await admin
          .from(table)
          .delete()
          .eq("user_id", userId);
        if (error) throw error;
      }

      const { error: deleteUserError } = await admin.auth.admin.deleteUser(userId);
      if (deleteUserError) throw deleteUserError;

      return Response.json({ deleted: true });
    } catch (error) {
      console.error("delete-my-account failed", error);
      return Response.json(
        {
          error:
            error instanceof Error ? error.message : "Account deletion failed.",
        },
        { status: 500 },
      );
    }
  }),
};
