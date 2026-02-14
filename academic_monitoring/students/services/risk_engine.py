def calculate_academic_risk(cgpa, attendance_percentage, fail_count, mid_avg=None):

    risk_score = 0.0

    if cgpa < 6.0:
        risk_score += 0.5
    elif cgpa < 7.5:
        risk_score += 0.25

    if attendance_percentage < 65:
        risk_score += 0.4
    elif attendance_percentage < 80:
        risk_score += 0.2

    if fail_count >= 1:
        risk_score += 0.4

    if mid_avg is not None and mid_avg < 20:
        risk_score += 0.2

    risk_score = min(risk_score, 1.0)

    if risk_score >= 0.7:
        return "HIGH", round(risk_score, 2)
    elif risk_score >= 0.4:
        return "MEDIUM", round(risk_score, 2)
    else:
        return "LOW", round(risk_score, 2)
