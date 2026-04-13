def extract_patient_context(patient):
    if not patient:
        return {}

    history = patient.get("basic_medical_history", {}) or {}
    visits = patient.get("previous_visits", []) or []

    return {
        "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or "Not specified",
        "age": patient.get("age") or history.get("age") or "Not specified",
        "sex": patient.get("sex") or history.get("sex") or "Not specified",
        "dob": patient.get("date_of_birth") or "Not specified",
        "history": history,
        "visits": visits[-3:] if visits else []
    }


def build_patient_context_text(patient):
    context = extract_patient_context(patient)

    if not context:
        return "No patient information available."

    history = context["history"]
    visits = context["visits"]

    if isinstance(history, dict) and history:
        history_text = "\n".join(f"- {key}: {value}" for key, value in history.items())
    else:
        history_text = "Not specified"

    visit_lines = []
    for visit in visits:
        date = visit.get("date", "Unknown date")
        soap = visit.get("soap_note", {}) or {}
        assessment = soap.get("assessment", "No assessment recorded")
        plan = soap.get("plan", "")
        visit_lines.append(f"- {date}: Assessment: {assessment}. Plan: {plan}")

    visit_text = "\n".join(visit_lines) if visit_lines else "No recent visits."

    return f"""
Patient Demographics:
- Name: {context['name']}
- Age: {context['age']}
- Sex: {context['sex']}
- DOB: {context['dob']}

Medical History:
{history_text}

Recent Visits Summary:
{visit_text}
""".strip()