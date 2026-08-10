# FA Library Backend

Flask + MySQL API for the FA Library frontend.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in local credentials.
4. Run `flask db init`, `flask db migrate -m "create fa_cases"`, and `flask db upgrade`.
5. Start with `flask run`.

Health check: `GET http://127.0.0.1:5000/api/v1/health`.
