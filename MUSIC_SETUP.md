# My Soundtrack setup

My Soundtrack gives each signed-in golfer a private music library. A golfer can
upload an MP3, M4A, or WAV file up to 6 MB, name the artist and playlist, listen
through a temporary signed link, and delete the track.

## One-time Supabase setup

1. Open the My Play project in Supabase.
2. Open **SQL Editor** and create a new query.
3. Paste all of `supabase/music_setup.sql` into the query.
4. Select **Run**. The query creates the `music_tracks` table, its per-user Row
   Level Security rules, and the private `Golf-Music` Storage bucket.
5. Open **Edge Functions**, edit `delete-my-account`, and replace its code with
   `supabase/functions/delete-my-account/index.ts`.
6. Deploy the function again. This makes account deletion remove private music
   files and music metadata along with the golfer's other data.

## App update

Upload the new `app.py` to the root of the GitHub repository and commit it. The
Streamlit app will redeploy from the new commit.

## Content rule

Only upload audio you own or have permission to store and play. The Tee-Bot
starter station is planned for a later release and is not enabled by this setup.
