# Automatic My Play account deletion

Deploy this as a protected Supabase Edge Function named `delete-my-account`.
It verifies the caller's access token, removes the caller's My Play rows and
private swing videos, and then deletes the Supabase Auth user.

The `SUPABASE_SERVICE_ROLE_KEY` is supplied by Supabase inside the Edge Function.
Never add that key to `app.py`, Streamlit secrets, or GitHub.

Before production use, test deletion with a disposable account and confirm that
every My Play table uses `user_id` for ownership. Add any future user-data tables
to the deletion list in `index.ts`.
