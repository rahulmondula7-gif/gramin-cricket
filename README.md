# Gramin Cricket — ग्रामीण क्रिकेट स्पर्धा

Responsive team registration website with FastAPI backend and Supabase database. It supports team name, village, captain name, mobile number, optional manager, confirmed registrations, waiting list, and a live list from the database.

## 1. Set up Supabase
1. Create a project at https://supabase.com/.
2. Open **SQL Editor** and run `database/01_schema.sql`.
3. Optional: run `database/02_seed.sql` for sample/demo records. Remove sample records before a real event.
4. In Project Settings → API, copy the project URL and **service_role** key. Keep the service-role key private.

## 2. Configure backend (Windows PowerShell)
```powershell
cd gramin-cricket\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```
Replace `SUPABASE_URL` and `SUPABASE_KEY` in `.env` with your own values. Do not share `.env` or publish the service-role key. For production, keep this key only on the backend host.

Start the API:
```powershell
python -m uvicorn main:app --reload --port 8000
```
API docs: http://127.0.0.1:8000/docs

## 3. Start frontend
Open a second PowerShell window:
```powershell
cd gramin-cricket\frontend
python -m http.server 5500
```
Open http://127.0.0.1:5500

## Important before public launch
- The frontend currently displays captain phone numbers publicly because that was requested. Get clear consent from each captain; otherwise hide phone numbers from the public list and show them only in an organizer dashboard.
- The demo has no organizer login/dashboard. The PATCH endpoint can change team status and should be protected by organizer authentication before public deployment.
- The confirmed/waiting capacity check is suitable as a starter, but simultaneous sign-ups can race. For a high-traffic event, move capacity allocation into a PostgreSQL transaction/function.
- Deploy the backend to a host that supports Python/FastAPI and the frontend to a static host. Then update `API_BASE` in `frontend/js/app.js` to the deployed HTTPS API URL and set `FRONTEND_ORIGIN` in backend `.env` to the deployed frontend origin.
- Public lists containing mobile numbers expose personal information. Publish only with informed permission.
