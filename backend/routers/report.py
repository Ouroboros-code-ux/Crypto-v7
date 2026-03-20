import time
import json
import logging
from google import genai
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report, ReportLog, User
from ..internal_types import ReportRequest
from ..services.blockchain import fetch_chain_history
from ..limiter import limiter
from ..config import GEMINI_API_KEY

from .auth import get_optional_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/report")
@limiter.limit("5/minute")
def report_address(request: Request, report: ReportRequest, db: Session = Depends(get_db), current_user = Depends(get_optional_user)):

    if not report.address or not report.reason:
        raise HTTPException(status_code=400, detail="Missing data")
    
    username = current_user.username

    existing_report = db.query(ReportLog).filter(
        ReportLog.username == username, 
        ReportLog.address == report.address.lower()
    ).first()
    
    if existing_report:
        raise HTTPException(status_code=400, detail="Address already reported.")
    
    heuristic_verified = False
    verification_reason = "Pending verification"
    
    if len(report.description) < 10:
        logger.info(f"Report skipped: Description too short from {username}")
        verification_reason = "Description too short."

    elif not report.address.startswith("0x") or len(report.address) != 42:
         verification_reason = "Invalid format."
    
    else:
        heuristic_verified = True
        verification_reason = "Heuristic checks passed."

    ai_verified = False
    
    if heuristic_verified and GEMINI_API_KEY:
        try:
            txs = fetch_chain_history(report.address, "ETH")
            client = genai.Client(api_key=GEMINI_API_KEY)
            model_id = 'gemini-1.5-flash'
            
            def sanitize_input(text: str) -> str:
                 
                 safe = text.replace("{", "").replace("}", "").replace("\"", "'").replace("\\", "").replace("`", "")
                 
                 safe = " ".join(safe.split())
                 return safe[:500]

            safe_description = sanitize_input(report.description)

            prompt = f"""
            User Report Verification Task:
            User '{report.username}' is reporting address '{report.address}' as a '{report.scam_type}'.
            User Description: "{safe_description}"
            Transaction Snapshot (First 5): {str(txs[:5]) if txs else 'No High Level Data'}
            
            Task: Determine if this report seems plausible based on the description and history.
            Return JSON: {  "verified": boolean, "reason": "concise summary" } 
            """
            
            result = client.models.generate_content(
                model=model_id,
                contents=prompt, 
                config={
                    "response_mime_type": "application/json"
                }
            )
            data = json.loads(result.text)
            
            ai_verified = data.get("verified", False)
            if ai_verified:
                verification_reason = data.get("reason", "Verified by AI.")
            else:
                 verification_reason = data.get("reason", "AI could not verify.")
                 
        except Exception as e:
            logger.error(f"AI verification service unavailable: {e}")
            ai_verified = False 
            verification_reason = f"AI Analysis failed: {str(e)[:100]}. Manual review required."

    final_verification = ai_verified if GEMINI_API_KEY else False 
 
    if final_verification:
        
        existing_global = db.query(Report).filter(Report.address == report.address.lower()).first()
        if existing_global:
            existing_global.reason = f"{report.scam_type}: {report.reason}"
            existing_global.timestamp = int(time.time())
        else:
            new_global_report = Report(
                address=report.address.lower(),
                reason=f"{report.scam_type}: {report.reason}",
                timestamp=int(time.time())
            )
            db.add(new_global_report)

        status_msg = f"Report verified. Address flagged."
    else:
        status_msg = f"Report received. Pending review."
    
    new_log = ReportLog(
        username=username,
        address=report.address.lower(),
        reason=report.reason,
        timestamp=int(time.time()),
        verified=1 if final_verification else 0
    )
    db.add(new_log)
    db.commit()
    
    return {"status": "success", "msg": status_msg, "verified": final_verification}