import pandas as pd
import json
from expert_ai import call_expert_ai
from traffic_controller import get_risk_status

# Load data
claims = pd.read_csv('claims/claims.csv')
history = pd.read_csv('claims/user_history.csv')

results = []
for _, row in claims.iterrows():
    # 1. Risk Assessment
    risk = get_risk_status(row['user_id'], history)
    
    # 2. Logic for Decision
    if risk == 'manual_review_required':
        verdict = "manual_review (risk)"
        ai_data = {"verdict": "N/A", "confidence": 0.0}
    else:
        ai_raw = call_expert_ai(row['image_paths'], row['user_claim'])
        try:
            ai_data = json.loads(ai_raw)
            if ai_data.get('confidence', 0) < 0.50:
                verdict = "manual_review (low_confidence)"
            else:
                verdict = ai_data.get('verdict', 'processed')
        except:
            verdict = "error"
            ai_data = {"verdict": "error", "confidence": 0.0}

    # 3. Build Full Table Row
    entry = {
        "user_id": row['user_id'],
        "image_paths": row['image_paths'],
        "user_claim": row['user_claim'],
        "claim_object": row['claim_object'],
        "evidence_standard_met": "yes" if verdict == "approved" else "no",
        "evidence_standard_met_reason": verdict,
        "risk_flags": risk,
        "issue_type": "N/A",
        "object_part": "N/A",
        "claim_status": verdict,
        "claim_status_justification": f"Confidence: {ai_data.get('confidence', 0)}",
        "supporting_image_ids": row['image_paths'],
        "valid_image": "True",
        "severity": "N/A"
    }
    results.append(entry)

# Save as CSV
pd.DataFrame(results).to_csv('claims/output.csv', index=False)
print("Orchestration complete! Check claims/output.csv for the new table format.")
