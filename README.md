# AIME — AI for Mood & Emotions

AIME is a Flask-based multimodal emotion analysis app with:
- Real audio model inference (`models/audio_emotion_model.h5`)
- Real video model inference (`models/video_emotion_model.h5`)
- Authentication + account sessions
- Persistent database-backed analysis history
- Analytics and exports

## Tech stack
- Python, Flask, SQLAlchemy, Flask-Migrate
- TensorFlow/Keras, Librosa, OpenCV
- Jinja templates + JS frontend

## Local setup (Linux/macOS)
```bash
git clone <repo-url>
cd AIME
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app webapp_v1/app.py db upgrade
python webapp_v1/app.py
```

## Local setup (Windows PowerShell)
```powershell
git clone <repo-url>
cd AIME
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
flask --app webapp_v1/app.py db upgrade
python webapp_v1/app.py
```

App URL: `http://localhost:5000`

## Environment variables
See `.env.example` for all required configuration.

## Database
- Default local database: SQLite (`webapp_v1/aime.db`)
- Production recommendation: PostgreSQL (`DATABASE_URL=postgresql+psycopg://...`)
- Run migrations with Flask-Migrate (`flask --app webapp_v1/app.py db ...`)

## Core API prefix
`/api/v1`

Key groups:
- `/auth/*` register/login/logout/me/password/session/account
- `/analysis/*` audio/video prediction, save/get/delete, notes
- `/history` list/filter/paginate + `/history/export`
- `/analytics/summary`, `/dashboard/summary`
- `/users/profile`, `/users/preferences`, `/users/export`

## Security notes
- Password hashing: Argon2
- Server-side session records with revocation + expiry
- Auth endpoint rate limiting
- Ownership checks on analysis resources
- Upload size limits

## Important disclaimer
AIME predictions are probabilistic estimates and **not** medical diagnosis.

## Deployment notes
- Frontend+backend can run together on Flask hosting.
- For scale, host backend on a Python platform and database on managed PostgreSQL.
- Configure production HTTPS, secure cookies, and production `SECRET_KEY`/`DATABASE_URL`.
