# Context-Aware Feature Labels
# Structure: "Feature": {"strength": "Label for Good", "risk": "Label for Bad"}
FEATURE_LABELS = {
    "CGPA": {
        "strength": "Good Grades (CGPA)",
        "risk": "Low Academic Performance (CGPA)"
    },
    "Attendance %": {
        "strength": "High Attendance",
        "risk": "Low Attendance"
    },
    "Failed Subjects": {
        "strength": "No Recent Failures",
        "risk": "Subject Failures/Backlogs"
    },
    "Mid Avg": {
        "strength": "Good Internal Marks",
        "risk": "Low Internal Marks"
    },
    "Total Subjects": {
        "strength": "Manageable Course Load",
        "risk": "High Course Load"
    }
}

def get_feature_label(feature_name, context_type):
    """
    Returns a human-readable label for the feature based on context.
    context_type: 'strength' or 'risk'
    """
    if feature_name in FEATURE_LABELS:
        return FEATURE_LABELS[feature_name].get(context_type, feature_name)
    return feature_name

def generate_risk_message(risk_level, explanation):
    """
    Converts SHAP explanation dict into a user-friendly strings.
    Handles 'Low', 'Medium', 'High' risk contexts.
    """
    if not explanation:
        return "Risk explanation is not available at the moment."

    # 1. Filter out noise (very small values)
    # Lowered threshold to 0.02 to catch "Medium" risk factors
    significant_features = {k: v for k, v in explanation.items() if abs(v) > 0.02}

    if not significant_features:
        # Fallback if everything is neutral
        if risk_level == "LOW":
            return "✅ Your academic performance is stable with no significant risk factors."
        elif risk_level == "MEDIUM":
            return "⚠️ Your performance is balanced but requires consistency to improve."
        else:
            return "⚠️ Multiple minor factors are contributing to academic risk. Please review your overall performance."

    # 2. Sort by impact (magnitude)
    sorted_features = sorted(significant_features.items(), key=lambda x: abs(x[1]), reverse=True)
    
    # 3. Categorize into Strengths vs Risks based on SIGN and RISK LEVEL
    strengths = []
    risks = []

    for feature, shap_value in sorted_features:
        if risk_level == "LOW":
            # For LOW Risk:
            # Positive SHAP (pushes towards Low Risk class) = Strength
            # Negative SHAP (pushes away from Low Risk class) = Risk/Warning
            if shap_value > 0:
                label = get_feature_label(feature, 'strength')
                strengths.append(label)
            else:
                label = get_feature_label(feature, 'risk')
                risks.append(label)
                
        else:
            # For HIGH / MEDIUM Risk:
            # Positive SHAP (pushes towards High/Med Risk) = Risk Factor
            # Negative SHAP (pushes away from High/Med Risk) = Mitigating Strength
            if shap_value > 0:
                label = get_feature_label(feature, 'risk')
                risks.append(label)
            else:
                label = get_feature_label(feature, 'strength')
                strengths.append(label)

    # 4. Construct the Message
    parts = []

    # Strategy: Prioritize the dominant category
    if risk_level == "LOW":
        if strengths:
            parts.append(f"🌟 Key strengths: {', '.join(strengths[:3])}")
        if risks:
            parts.append(f"⚠️ Areas to watch: {', '.join(risks[:2])}")
            
    elif risk_level == "HIGH":
        if risks:
            parts.append(f"📉 Risk increased due to: {', '.join(risks[:3])}")
        if strengths:
            parts.append(f"📈 Mitigating factors: {', '.join(strengths[:2])}")
            
    else: # MEDIUM
        # Balanced view
        if risks:
            parts.append(f"📉 Main concerns: {', '.join(risks[:2])}")
        if strengths:
            parts.append(f"📈 Positive aspects: {', '.join(strengths[:2])}")
        
        if not parts:
            parts.append("⚠️ Your academic profile shows mixed signals.")

    return " ".join(parts)
