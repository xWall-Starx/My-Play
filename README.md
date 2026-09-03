# My Play

My Play is an AI-assisted personal golf caddie that learns a golfer's real bag,
distances, tendencies, preferences, shots, and rounds. It combines that player
model with live conditions to recommend a club, playing distance, target line,
safe miss, strategy, and confidence.

The project is currently a public beta.

## Core experience

- Build a personal golfer and golf-bag profile.
- Navigate from a clickable high-tech clubhouse with selectable scenery.
- Choose **Play**, then keep Course rounds and Driving Range sessions distinct.
- Record rounds and individual range or course shot results.
- Import simulator and scorecard data.
- Ask the caddie by voice or manual input.
- Store and play a private, rights-confirmed golf soundtrack by playlist.
- Build a general game-day fuel plan and optionally keep a private meal,
  snack, and hydration log.
- Complete a voluntary Performance Check-In for sleep and readiness, with a
  separate explicit choice controlling whether the caddie may use it.
- Review player, club, and round analytics.
- Export core account data from Settings.
- Change a password or permanently delete an account from Settings.

## Run locally

Install the dependencies, configure Supabase and OpenAI secrets, and run:

```bash
streamlit run app.py
```

## Deploy

Deploy `app.py` from this repository to Streamlit Community Cloud. Keep API keys
in Streamlit Secrets—never commit `.streamlit/secrets.toml`.

The self-service deletion button calls the protected Supabase Edge Function at
`supabase/functions/delete-my-account/index.ts`. Deploy that function in the
same Supabase project before enabling public accounts. Test the full flow with a
disposable account first.

The private music room requires a one-time database and Storage setup. Run
`supabase/music_setup.sql` in the Supabase SQL Editor, then redeploy the account
deletion function so deleting an account also removes its private music files.
The Tee-Bot starter station is intentionally reserved for a later release.

The optional Fuel Log also requires a one-time setup. Run
`supabase/nutrition_setup.sql` in the Supabase SQL Editor, then use the latest
account-deletion function. See `FUEL_SETUP.md` for the public-beta checklist.

## Privacy and beta terms

The account-creation and Settings screens contain the current Privacy & Data
Notice and Beta Terms. Privacy, support, and deletion questions can be sent to
`Staticprophet77@gmail.com`.

## License

MIT — see `LICENSE`.

Before deploying, copy the contents of your local:

`.streamlit/secrets.toml`

into:

Streamlit Community Cloud → App settings → Secrets

Do not upload `secrets.toml` to GitHub.

## Main dependencies

Dependencies are listed in `requirements.txt`.
