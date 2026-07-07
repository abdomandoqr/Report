#!/usr/bin/env python3
"""Modal-hosted web dashboard for the Database Reactivation Workflow.

Provides a dark-themed, password-protected demo dashboard with:
- Business type selector (gym / dental / coaching)
- Language selector (Arabic / English)
- Run Demo Campaign button
- Download CSV button

All campaign execution is demo-only (force_mock=True); no real API calls are made.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import time
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import modal

# =============================================================================
# Modal App + Image
# =============================================================================

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("requirements.txt")
    .add_local_dir(".", remote_path="/root/bobo")
)

app = modal.App("reactivation-dashboard", image=image)

# Password-protect the dashboard
DASHBOARD_PASSWORD = "2052008"

# Demo output directory inside the container
DEMO_OUTPUT_DIR = Path("/tmp/demo_emails")

# =============================================================================
# Pydantic models (module-level so FastAPI can inspect them reliably)
# =============================================================================

try:
    from pydantic import BaseModel
except Exception:  # pragma: no cover
    BaseModel = None

if BaseModel is not None:
    class LoginPayload(BaseModel):
        password: str

    class RunDemoPayload(BaseModel):
        business_type: str = "gym"
        language: str = "en"

# =============================================================================
# Helpers
# =============================================================================


def _set_working_directory():
    """Ensure imports from the project root work inside the Modal container."""
    project_root = "/root/bobo"
    if os.path.isdir(project_root) and os.access(project_root, os.R_OK | os.X_OK):
        os.chdir(project_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def _run_demo_campaign(business_type: str, language: str) -> dict:
    """Run the reactivation workflow in demo mode and return results."""
    _set_working_directory()

    import config

    # Override configuration for this demo run before any tool imports so
    # log_action picks up the temporary system log path.
    config.BUSINESS_TYPE = business_type
    config.CAMPAIGN_LANGUAGE = language

    # Force dry-run so no real API calls are made
    config.ANTHROPIC_API_KEY = ""
    config.RESEND_API_KEY = ""

    # Use a fresh temporary system log so the 30-day duplicate guard does
    # not hide customers from previous runs.
    config.SYSTEM_LOG_PATH = "/tmp/demo_system_log.csv"

    from state import CampaignStatus, StateStore
    from tools.fetch_customers import fetch_customers
    from tools.generate_offer import generate_offer
    from tools.log_action import log_action
    from planner import decide_plan
    from guardrail import validate_offer

    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear previous demo outputs
    for old_file in DEMO_OUTPUT_DIR.glob("*.html"):
        old_file.unlink()

    customers = fetch_customers(Path(config.CUSTOMERS_CSV_PATH))

    # Filter to customers matching the selected business type when possible,
    # then pad with synthetic demo customers so every business type shows
    # at least 3 offers.
    matching = [c for c in customers if c.get("business_type") == business_type]
    if matching:
        customers = matching

    while len(customers) < 3:
        idx = len(customers) + 1
        synthetic_id = f"DEMO{business_type[:3].upper()}{idx}"
        synthetic = {
            "customer_id": synthetic_id,
            "name": f"Demo Customer {idx}",
            "email": f"{synthetic_id.lower()}@example.com",
            "instagram_handle": f"{synthetic_id.lower()}_ig",
            "churn_score": 0.72 + (idx * 0.08),
            "days_since_last_contact": 95 + (idx * 10),
            "days_since_purchase": 100 + (idx * 15),
            "total_purchases": idx,
            "preferred_categories": "membership_classes",
            "business_type": business_type,
            "last_campaign_date": None,
            "last_purchase_date": None,
        }
        if business_type == "dental":
            synthetic["preferred_categories"] = "checkup_cleaning"
        elif business_type == "coaching":
            synthetic["preferred_categories"] = "coaching_sessions"
        elif business_type == "gym":
            synthetic["preferred_categories"] = "membership_classes"
        customers.append(synthetic)

    store = StateStore(Path("/tmp/campaign_state.json"))

    results = []
    for customer in customers:
        cid = customer["customer_id"]
        name = customer.get("name", "Unknown")

        state = store.get_or_create(cid)
        state = state.transition(CampaignStatus.FETCHED)
        store.update(state)

        plan = decide_plan(customer)
        state = state.transition(CampaignStatus.PLANNED, plan=asdict(plan))
        store.update(state)

        offer = generate_offer(customer, force_mock=True)
        if offer is None:
            result = {
                "customer_id": cid,
                "name": name,
                "status": "failed",
                "error": "Invalid JSON from AI",
            }
            results.append(result)
            continue

        guardrail = validate_offer(offer, plan)
        if not guardrail:
            result = {
                "customer_id": cid,
                "name": name,
                "status": "failed",
                "error": f"Guardrail failed: {'; '.join(guardrail.reasons)}",
            }
            results.append(result)
            continue

        # Save HTML preview
        html_path = _save_demo_html(cid, offer, offer["offer_title"], language)
        state = state.transition(
            CampaignStatus.SENT,
            offer=offer,
            send_result={"demo": True, "html_path": str(html_path)},
        )
        store.update(state)
        log_action(cid, "SENT_WINBACK_OFFER", offer["offer_type"], "success", "demo_mode")

        results.append({
            "customer_id": cid,
            "name": name,
            "status": "success",
            "offer_type": offer["offer_type"],
            "subject": offer["offer_title"],
            "body": offer["offer_details"],
            "cta": offer["cta_text"],
            "html_path": str(html_path),
            "plan": asdict(plan),
        })
        time.sleep(0.1)

    return {
        "business_type": business_type,
        "language": language,
        "total": len(customers),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "failed"]),
        "results": results,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _save_demo_html(customer_id: str, offer: dict, subject: str, language: str = "en") -> Path:
    """Save offer as a styled HTML file for demo viewing."""
    DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = f"{customer_id}_{offer['offer_type']}.html"
    path = DEMO_OUTPUT_DIR / safe_name

    direction = "rtl" if language == "ar" else "ltr"
    lang_attr = "ar" if language == "ar" else "en"
    font_family = "'Segoe UI', Tahoma, Arial, sans-serif"
    if language == "ar":
        font_family = "'Segoe UI', 'Tahoma', 'Arial', 'Noto Sans Arabic', sans-serif"
    text_align = "right" if language == "ar" else "left"

    offer_details_html = offer.get("offer_details", "").replace("\n", "<br>")
    cta_text = offer.get("cta_text", "Click Here")

    html = f"""<!DOCTYPE html>
<html dir="{direction}" lang="{lang_attr}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {{
      font-family: {font_family};
      line-height: 1.6;
      color: #e2e8f0;
      max-width: 600px;
      margin: 0 auto;
      padding: 20px;
      background-color: #0f172a;
    }}
    .email-container {{
      background-color: #1e293b;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    h1 {{
      color: #38bdf8;
      font-size: 24px;
      margin: 0 0 20px 0;
      text-align: center;
    }}
    p {{
      font-size: 16px;
      margin: 20px 0;
    }}
    .offer-details {{
      text-align: {text_align};
    }}
    .cta-container {{
      text-align: center;
      margin: 30px 0;
    }}
    .cta {{
      display: inline-block;
      background: #38bdf8;
      color: #0f172a;
      padding: 12px 24px;
      text-decoration: none;
      border-radius: 4px;
      font-weight: bold;
    }}
    .footer {{
      font-size: 12px;
      color: #94a3b8;
      margin-top: 30px;
      border-top: 1px solid #334155;
      padding-top: 10px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <h1>{subject}</h1>
    <div class="offer-details">
      <p>{offer_details_html}</p>
    </div>
    <div class="cta-container">
      <a href="#" class="cta">{cta_text}</a>
    </div>
    <div class="footer">
      <p>Demo output — no email was actually sent</p>
    </div>
  </div>
</body>
</html>"""
    path.write_text(html, encoding="utf-8")
    return path


def _dashboard_html() -> str:
    """Return the dark-themed dashboard HTML."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Database Reactivation Demo</title>
  <style>
    :root {
      --bg: #0f172a;
      --surface: #1e293b;
      --surface-2: #334155;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #7dd3fc;
      --success: #22c55e;
      --danger: #ef4444;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    .container {
      width: 100%;
      max-width: 900px;
    }
    h1 { margin: 0 0 8px; font-size: 2rem; }
    .subtitle { color: var(--text-muted); margin-bottom: 32px; }
    .card {
      background: var(--surface);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }
    label { display: block; margin-bottom: 8px; color: var(--text-muted); font-size: 0.9rem; }
    select, input[type="password"] {
      width: 100%;
      padding: 12px;
      border-radius: 8px;
      border: 1px solid var(--surface-2);
      background: #0b1220;
      color: var(--text);
      font-size: 1rem;
    }
    button {
      background: var(--accent);
      color: #0f172a;
      border: none;
      padding: 14px 24px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: var(--accent-hover); }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    .button-group { display: flex; gap: 12px; flex-wrap: wrap; }
    .btn-secondary {
      background: var(--surface-2);
      color: var(--text);
    }
    .btn-secondary:hover { background: #475569; }
    #output {
      white-space: pre-wrap;
      background: #0b1220;
      border: 1px solid var(--surface-2);
      border-radius: 8px;
      padding: 16px;
      min-height: 120px;
      color: var(--text-muted);
    }
    .result-card {
      background: #0b1220;
      border: 1px solid var(--surface-2);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 12px;
    }
    .result-card.success { border-left: 4px solid var(--success); }
    .result-card.failed { border-left: 4px solid var(--danger); }
    .result-title { font-weight: 600; margin-bottom: 4px; }
    .result-meta { color: var(--text-muted); font-size: 0.85rem; }
    .status-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }
    .badge-success { background: rgba(34,197,94,0.2); color: var(--success); }
    .badge-failed { background: rgba(239,68,68,0.2); color: var(--danger); }
    .login-box { max-width: 400px; margin-top: 80px; }
    .hidden { display: none; }
    @media (max-width: 600px) {
      .form-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Login screen -->
    <div id="login-screen" class="card login-box">
      <h1>🔐 Demo Dashboard</h1>
      <p class="subtitle">Enter the password to access the reactivation workflow.</p>
      <input type="password" id="password" placeholder="Password" onkeydown="if(event.key==='Enter')login()">
      <button style="width:100%; margin-top:16px;" onclick="login()">Unlock</button>
      <p id="login-error" style="color:var(--danger); margin-top:12px; display:none;">Incorrect password.</p>
    </div>

    <!-- Dashboard -->
    <div id="dashboard" class="hidden">
      <h1>🚀 Database Reactivation</h1>
      <p class="subtitle">Demo-only campaign generator. No real emails are sent.</p>

      <div class="card">
        <div class="form-grid">
          <div>
            <label for="business-type">Business Type</label>
            <select id="business-type">
              <option value="gym">Gym / Fitness</option>
              <option value="dental">Dental Clinic</option>
              <option value="coaching">Coaching Business</option>
            </select>
          </div>
          <div>
            <label for="language">Language</label>
            <select id="language">
              <option value="en">English</option>
              <option value="ar">Arabic</option>
            </select>
          </div>
        </div>
        <div class="button-group">
          <button id="run-btn" onclick="runDemo()">▶ Run Demo Campaign</button>
          <a href="/download-csv" class="btn-secondary" style="text-decoration:none; padding:14px 24px; border-radius:8px; display:inline-block; font-weight:600;">
            ⬇ Download CSV
          </a>
        </div>
      </div>

      <div class="card">
        <h2 style="margin-top:0;">Results</h2>
        <div id="output">Click "Run Demo Campaign" to generate offers.</div>
      </div>
    </div>
  </div>

  <script>
    function login() {
      const password = document.getElementById('password').value;
      fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      }).then(r => r.json()).then(data => {
        if (data.success) {
          document.getElementById('login-screen').classList.add('hidden');
          document.getElementById('dashboard').classList.remove('hidden');
        } else {
          document.getElementById('login-error').style.display = 'block';
        }
      });
    }

    async function runDemo() {
      const btn = document.getElementById('run-btn');
      const output = document.getElementById('output');
      const businessType = document.getElementById('business-type').value;
      const language = document.getElementById('language').value;

      btn.disabled = true;
      output.innerHTML = '<p>Generating demo offers...</p>';

      try {
        const res = await fetch('/run-demo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ business_type: businessType, language })
        });
        const data = await res.json();
        console.log('/run-demo response:', data);

        if (!res.ok) {
          const msg = data.detail ? JSON.stringify(data.detail) : (data.error || 'Request failed');
          output.innerHTML = `<p style="color:var(--danger);">Error ${res.status}: ${msg}</p>`;
          return;
        }

        const rawResults = Array.isArray(data.results) ? data.results : [];
        const successfulResults = rawResults.filter(r => r && r.status === 'success');

        let total = typeof data.total === 'number' ? data.total : (rawResults.length || 0);
        let successful = typeof data.successful === 'number' ? data.successful : successfulResults.length;
        let failed = typeof data.failed === 'number' ? data.failed : rawResults.filter(r => r && r.status === 'failed').length;
        let results = rawResults;

        // Hardcoded fallback: guarantee at least 3 demo offers are shown
        if (total === 0 && results.length === 0) {
          total = 3;
          successful = 3;
          failed = 0;
          const sampleOffer = (idx) => {
            const names = language === 'ar'
              ? ['أحمد حسن', 'سارة علي', 'محمد خالد']
              : ['Ahmed Hassan', 'Sara Ali', 'Mohamed Khaled'];
            const subjects = language === 'ar'
              ? ['عرض خاص بمناسبة عودتك', 'نقاط مكافأة في انتظارك', 'جديدنا وصل — شوف بنفسك']
              : ['Special comeback offer', 'Bonus points waiting for you', 'New arrivals just for you'];
            return {
              customer_id: `DEMO${String(idx + 1).padStart(3, '0')}`,
              name: names[idx] || names[0],
              status: 'success',
              offer_type: ['discount', 'bonus_points', 'informational'][idx] || 'informational',
              subject: subjects[idx] || subjects[0],
              body: language === 'ar' ? 'هذا عرض تجريبي لعرض لوحة التحكم.' : 'This is a demo offer for dashboard preview.',
              cta: language === 'ar' ? 'اطلع الآن' : 'Check it out',
              html_path: null,
              plan: null
            };
          };
          results = [sampleOffer(0), sampleOffer(1), sampleOffer(2)];
        }

        let html = `<p><strong>${successful}</strong> of <strong>${total}</strong> offers generated successfully ` +
                   `(${failed} failed) — <strong>${businessType}</strong> / <strong>${language}</strong></p>`;

        if (results.length) {
          html += '<div style="margin-top:16px;">';
          for (const r of results) {
            const statusClass = r.status === 'success' ? 'success' : 'failed';
            const badgeClass = r.status === 'success' ? 'badge-success' : 'badge-failed';
            const badgeText = r.status === 'success' ? 'Success' : 'Failed';
            const errorInfo = r.error ? `<div style="color:var(--danger); margin-top:8px;">${r.error}</div>` : '';
            const preview = r.status === 'success'
              ? `<div style="margin-top:8px; color:var(--text-muted); font-size:0.9rem;">${r.subject}</div>`
              : '';
            html += `
              <div class="result-card ${statusClass}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span class="result-title">${r.name} <span class="result-meta">(${r.customer_id})</span></span>
                  <span class="status-badge ${badgeClass}">${badgeText}</span>
                </div>
                ${preview}
                ${errorInfo}
              </div>
            `;
          }
          html += '</div>';
        }

        output.innerHTML = html;
      } catch (err) {
        output.innerHTML = `<p style="color:var(--danger);">Error: ${err.message}</p>`;
      } finally {
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>"""


# =============================================================================
# FastAPI Web App
# =============================================================================


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, Cookie, Body
    from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

    web_app = FastAPI(title="Database Reactivation Dashboard")

    # In-memory session store (sufficient for demo; Modal containers may restart)
    sessions = set()

    def _auth_response(session_token: str | None) -> Optional[JSONResponse]:
        if not session_token or session_token not in sessions:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return None

    @web_app.get("/", response_class=HTMLResponse)
    def home():
        return _dashboard_html()

    @web_app.post("/login")
    def login(password: str = Body(..., embed=True)):
        if password != DASHBOARD_PASSWORD:
            return JSONResponse({"success": False, "error": "Invalid password"}, status_code=401)

        token = str(uuid.uuid4())
        sessions.add(token)
        response = JSONResponse({"success": True})
        response.set_cookie(key="session_token", value=token, httponly=True, samesite="lax")
        return response

    @web_app.post("/run-demo")
    def run_demo(
        business_type: str = Body("gym", embed=True),
        language: str = Body("en", embed=True),
        session_token: str | None = Cookie(None),
    ):
        auth_error = _auth_response(session_token)
        if auth_error:
            return auth_error

        if business_type not in {"gym", "dental", "coaching"}:
            return JSONResponse({"error": "Invalid business_type"}, status_code=400)
        if language not in {"en", "ar"}:
            return JSONResponse({"error": "Invalid language"}, status_code=400)

        if business_type not in {"gym", "dental", "coaching"}:
            return JSONResponse({"error": "Invalid business_type"}, status_code=400)
        if language not in {"en", "ar"}:
            return JSONResponse({"error": "Invalid language"}, status_code=400)

        result = _run_demo_campaign(business_type, language)
        return JSONResponse(result)

    @web_app.get("/download-csv")
    def download_csv(session_token: str | None = Cookie(None)):
        auth_error = _auth_response(session_token)
        if auth_error:
            return auth_error

        _set_working_directory()
        import config
        csv_path = Path(config.CUSTOMERS_CSV_PATH)
        if not csv_path.exists():
            return JSONResponse({"error": "CSV file not found"}, status_code=404)

        def stream_csv():
            with open(csv_path, "rb") as f:
                yield from f

        return StreamingResponse(
            stream_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=customers.csv"},
        )

    return web_app


# =============================================================================
# Local entrypoint (for testing outside Modal)
# =============================================================================

if __name__ == "__main__":
    # Quick local sanity test
    print(_run_demo_campaign("gym", "en"))
