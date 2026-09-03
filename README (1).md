# My Play

My Play is an AI-assisted personal golf caddie that learns a golfer's real bag,
distances, tendencies, preferences, shots, and rounds. It combines that player
model with live conditions to recommend a club, playing distance, target line,
safe miss, strategy, and confidence.

The project is currently a public beta.

## Core experience

- Build a personal golfer and golf-bag profile.
- Navigate from a clickable high-tech clubhouse with selectable scenery.
- Record rounds and individual shot results.
- Import simulator and scorecard data.
- Ask the caddie by voice or manual input.
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
