# Fuel room setup

The Fuel room provides general game-day planning, an optional private log for
meals, snacks, water, and sports drinks, and a voluntary Performance Check-In
for sleep, energy, stress, mood, and soreness. It does not diagnose, prescribe,
or replace advice from a qualified health professional.

## One-time Supabase setup

1. Open the My Play project in Supabase.
2. Open **SQL Editor** and create a new query.
3. Paste all of `supabase/nutrition_setup.sql` into the query.
4. Select **Run**. This creates the `nutrition_logs` and
   `performance_checkins` tables and per-user Row Level Security rules so
   signed-in golfers can access only their own entries.
5. Open **Edge Functions**, edit `delete-my-account`, and replace its code with
   `supabase/functions/delete-my-account/index.ts`.
6. Deploy the function again so account deletion also removes Fuel Log entries.

## Public-beta checklist

- Test save, view, export, and delete with a disposable account.
- Confirm one test account cannot read another account's Fuel Log.
- Keep the in-app non-medical disclaimer visible.
- Never hide wellness collection or silently infer behavioral-health status.
- Keep caddie use off unless the golfer affirmatively enables it per check-in.
- Do not add medical diagnoses, supplement prescriptions, or personalized
  treatment claims without qualified professional and legal review.
