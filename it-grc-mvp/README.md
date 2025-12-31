# IT GRC MVP (Backend)

IT GRC MVP is a FastAPI backend that models users, risks, access requests, compliance items, and audit trails.

## Quickstart
### Prerequisites
- Python 3.11+
- PostgreSQL 14+

### Run locally
```bash
cd backend
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

## Configuration
- `DATABASE_URL` (update the placeholder password in `.env`)
- `JWT_SECRET` (placeholder in `.env.example`, update before real use)
- `JWT_ALG`, `ACCESS_TOKEN_MINUTES`

## Demo users
The seed script creates demo users with the placeholder password `ChangeMe123!`. Change this in `backend/app/seed.py` before any real use.

## Tests
```bash
python -m unittest discover -s tests
```
