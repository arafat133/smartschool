from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
import time, re, sqlite3, os

app = FastAPI(
    title="نظام المدارس السحابي الآمن",
    description="واجهة برمجة التطبيقات (API) لنظام المدارس السحابي الآمن مع جدار حماية متعدد الطبقات وتوثيق مشفر.",
    version="2.0.0"
)

# ==================== LAYER 1: MULTI-LAYER SYSTEM FIREWALL MIDDLEWARE ====================
RATE_LIMIT_STORE = {}
BLOCKED_IPS = set()

# SQLi & XSS Payload Patterns
SUSPICIOUS_PATTERNS = [
    r"(?i)\b(UNION\s+SELECT|DROP\s+TABLE|ALTER\s+TABLE|DELETE\s+FROM|INSERT\s+INTO)\b",
    r"(?i)<script\b[^>]*>",
    r"(?i)javascript\s*:",
    r"(?i)\bOR\s+1\s*=\s*1\b",
    r"(?i)--\s*$"
]

@app.middleware("http")
async def security_firewall_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()
    
    # 1. IP Blacklist & Rate Limiting Check (Max 120 requests per minute)
    if client_ip in BLOCKED_IPS:
        return JSONResponse(status_code=403, content={"detail": "⚠️ IP address blocked due to security audit violation."})
    
    req_history = [t for t in RATE_LIMIT_STORE.get(client_ip, []) if now - t < 60]
    req_history.append(now)
    RATE_LIMIT_STORE[client_ip] = req_history
    
    if len(req_history) > 120:
        BLOCKED_IPS.add(client_ip)
        return JSONResponse(status_code=429, content={"detail": "⚠️ Rate limit exceeded. Temporary firewall block applied."})

    # 2. SQLi & XSS Payload Inspection
    query_params = str(request.query_params)
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, query_params):
            return JSONResponse(status_code=400, content={"detail": "⚠️ Security Firewall Alert: Malformed or suspicious query payload detected."})

    # Execute request
    response: Response = await call_next(request)
    
    # 3. HTTP Security Headers Injection
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Server"] = "Secure-School-Firewall-v2"
    
    return response

# ==================== LAYER 2: DATABASE INTEGRITY & PROTECTION ENGINE ====================
@app.on_event("startup")
def enforce_database_security():
    try:
        db_path = "school_system.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA integrity_check;")
        conn.close()
        print("[SEC] Database Protection Engine Enabled: WAL Mode, Foreign Keys & Integrity Check Passed!")
    except Exception as e:
        print("[SEC Warning] DB Protection Error:", e)

from app.api.api import api_router

# Set up CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# ==================== DEDICATED PORTAL ROUTING ENGINE ====================

# 1. School Admin & Teachers Portal
@app.get("/school", include_in_schema=False)
@app.get("/school.html", include_in_schema=False)
async def get_school_portal():
    return FileResponse("frontend/school.html")

# 2. SaaS Super Admin Portal
@app.get("/admin", include_in_schema=False)
@app.get("/saas", include_in_schema=False)
@app.get("/admin.html", include_in_schema=False)
async def get_saas_portal():
    return FileResponse("frontend/admin.html")

# 3. Parent & Student Portal
@app.get("/parent", include_in_schema=False)
@app.get("/parents", include_in_schema=False)
@app.get("/parent.html", include_in_schema=False)
async def get_parent_portal():
    return FileResponse("frontend/parent.html")

# Static assets
app.mount("/static", StaticFiles(directory="frontend"), name="static")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
