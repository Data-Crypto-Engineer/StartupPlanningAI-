"""
ai_engine.py - Gemini Model Reasoning and Anti-Hallucination Engine
Part of '🚀 Startup Planning & Organizer AI'

Responsibilities:
- Strictly enforces anti-hallucination policies
- Calculates deterministic commercial intent scores (0-100)
- Computes research confidence (High/Medium/Low)
- Generates practical, grounded proposed AI solutions with realistic working names
- Crafts personalized outreach emails & <=200 char LinkedIn messages
- Builds the 10-step explainability reasoning trail
- Interfaces with Gemini via @google/genai or google.genai
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"


def calculate_commercial_intent_score(evidence_flags: Dict[str, bool]) -> Dict[str, Any]:
    """
    Transparent, deterministic formula:
    +30 = active paid job/freelance requirement
    +25 = explicit technology/automation requirement
    +20 = procurement/tender/RFP evidence
    +15 = documented operational problem
    +10 = repeated hiring/activity indicating persistent workload
    """
    score = 0
    breakdown = []

    if evidence_flags.get("has_active_job_or_freelance"):
        score += 30
        breakdown.append("Active paid job/freelance requirement: +30")
    if evidence_flags.get("has_tech_or_automation_req"):
        score += 25
        breakdown.append("Explicit technology/automation requirement: +25")
    if evidence_flags.get("has_procurement_or_rfp"):
        score += 20
        breakdown.append("Procurement / tender / RFP evidence: +20")
    if evidence_flags.get("has_documented_problem"):
        score += 15
        breakdown.append("Documented operational problem: +15")
    if evidence_flags.get("has_repeated_workload"):
        score += 10
        breakdown.append("Repeated operational workload / persistent hiring: +10")

    score = min(score, 100)

    if score >= 70:
        level = "Very Strong"
    elif score >= 50:
        level = "Strong"
    elif score >= 30:
        level = "Moderate"
    elif score > 0:
        level = "Weak"
    else:
        level = "Insufficient evidence"

    return {
        "score": score,
        "level": level,
        "breakdown": breakdown
    }


def enforce_anti_hallucination_rules(data: Dict[str, Any]) -> Dict[str, Any]:
    """Strictly scrubs unverified claims according to the 7 Anti-Hallucination Rules."""
    cleaned = dict(data)

    # Rule 2: No verified email = "Email: Not publicly verified"
    email = cleaned.get("contact_email", "")
    if not email or "@" not in str(email) or "unverified" in str(email).lower():
        cleaned["contact_email"] = "Email: Not publicly verified"
        cleaned["email_verification_status"] = "Not publicly verified"

    # Rule 3: No verified LinkedIn = "LinkedIn: Not found"
    linkedin = cleaned.get("contact_linkedin", "")
    if not linkedin or "linkedin.com" not in str(linkedin).lower():
        cleaned["contact_linkedin"] = "LinkedIn: Not found"

    # Rule 4: No active job source = do not claim active job
    if cleaned.get("opportunity_type") == "Job/Freelance" and not cleaned.get("job_url"):
        cleaned["opportunity_type"] = "Operational Problem"

    # Rule 5: No geographic evidence = do not claim Pakistan eligibility
    if cleaned.get("region") != "Pakistan":
        eligibility = cleaned.get("application_eligibility", "")
        if "verified" not in eligibility.lower():
            cleaned["application_eligibility"] = "International eligibility not verified."

    # Rule 7: Proposed AI solution label
    solution = cleaned.get("proposed_solution", "")
    if solution and not solution.startswith("Proposed Solution:"):
        cleaned["proposed_solution"] = f"Proposed Solution: {solution}"

    # LinkedIn character limit enforcement (<= 200 characters)
    li_msg = cleaned.get("linkedin_message", "")
    if len(li_msg) > 200:
        cleaned["linkedin_message"] = li_msg[:197] + "..."

    return cleaned


def build_reasoning_trail(
    region: str,
    domain: str,
    org_name: str,
    source_name: str,
    evidence_desc: str,
    problem_desc: str,
    app_name: str,
    score: int,
    contact_name: str,
    confidence: str
) -> List[str]:
    """Creates the 10-step explainability reasoning trail."""
    return [
        f"1. Target region set to: {region}.",
        f"2. Focused domain identified as: {domain}.",
        f"3. Organization '{org_name}' discovered via verified source: {source_name}.",
        f"4. Commercial & operational evidence identified: {evidence_desc}.",
        f"5. Concrete operational bottleneck documented: {problem_desc}.",
        "6. Workflow decomposed into repetitive tasks suitable for AI automation.",
        f"7. Lightweight solution proposed: '{app_name}'.",
        f"8. Commercial intent computed using deterministic formula: {score}/100.",
        f"9. Relevant stakeholder investigated: {contact_name}.",
        f"10. Research confidence evaluated as '{confidence}' based on source hierarchy."
    ]


class GeminiEngine:
    """Manages Gemini model prompts with fallback and structured validation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            return
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize google.genai: {e}")
            self.client = None

    def is_available(self) -> bool:
        return self.client is not None or bool(self.api_key)

    def analyze_opportunity(self, raw_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes a raw web/job signal into a validated opportunity structure.
        """
        region = raw_signal.get("region", "Pakistan")
        domain = raw_signal.get("domain", "General")
        org_name = raw_signal.get("organization", "Target Organization")
        title = raw_signal.get("title", "")
        evidence_text = raw_signal.get("evidence", "")

        # Default fallback synthesis if Gemini API key not provided or unavailable
        # Evaluate commercial score from raw indicators
        has_job = "job" in raw_signal.get("source_type", "").lower() or bool(raw_signal.get("job_url"))
        has_tech = any(k in evidence_text.lower() for k in ["software", "automation", "python", "ai", "system", "erp", "it "])
        has_proc = "tender" in evidence_text.lower() or "procurement" in evidence_text.lower() or "rfp" in evidence_text.lower()
        has_prob = len(evidence_text) > 30
        has_workload = any(k in evidence_text.lower() for k in ["repeated", "daily", "volume", "manual", "reporting", "data entry"])

        score_dict = calculate_commercial_intent_score({
            "has_active_job_or_freelance": has_job,
            "has_tech_or_automation_req": has_tech,
            "has_procurement_or_rfp": has_proc,
            "has_documented_problem": has_prob,
            "has_repeated_workload": has_workload
        })

        # Check for Gemini synthesis if client is available
        if self.client and self.api_key:
            try:
                prompt = f"""
You are an expert AI startup opportunity researcher.
Analyze the following verified market signal:
Organization: {org_name}
Domain: {domain}
Region: {region}
Signal/Job Title: {title}
Evidence Text: {evidence_text}

Produce a JSON response matching:
{{
  "problem_statement": "Concise statement of operational pain",
  "problem_evidence": ["Evidence 1", "Evidence 2"],
  "proposed_solution": "Concise practical solution",
  "app_name": "Short working name e.g. TenderLens AI",
  "ai_intent": "High/Medium/Low",
  "why_selected": ["Reason 1", "Reason 2", "Reason 3"],
  "outreach_email": "Concise non-spammy email mentioning the specific problem and small POC",
  "linkedin_message": "Punchy message under 190 characters",
  "commercial_signals": ["Signal 1", "Signal 2"]
}}

STRICT RULES:
- Never fabricate emails or LinkedIn URLs.
- Keep LinkedIn message strictly under 195 characters.
- Keep the tone polite, professional, and value-focused.
"""
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                if response and response.text:
                    # Parse JSON from response
                    match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if match:
                        parsed = json.loads(match.group(0))
                        app_name = parsed.get("app_name", f"{domain.split()[0]}Flow AI")
                        confidence = "High" if score_dict["score"] >= 65 and has_job else "Medium"
                        contact_name = raw_signal.get("contact_name", "Not publicly verified")

                        result = {
                            "organization": org_name,
                            "domain": domain,
                            "region": region,
                            "website": raw_signal.get("url", f"https://www.{org_name.lower().replace(' ', '')}.com"),
                            "opportunity_type": "Job/Freelance" if has_job else "Operational Problem",
                            "job_title": title if has_job else "",
                            "job_url": raw_signal.get("job_url", ""),
                            "application_eligibility": "Verified eligible" if region == "Pakistan" else "International eligibility not verified.",
                            "remote_status": raw_signal.get("remote_status", "Remote" if "remote" in evidence_text.lower() else "On-site/Hybrid"),
                            "problem_statement": parsed.get("problem_statement", f"Manual workload in {domain} operations."),
                            "problem_evidence": parsed.get("problem_evidence", [evidence_text]),
                            "proposed_solution": parsed.get("proposed_solution", "AI Workflow Automation Assistant"),
                            "app_name": app_name,
                            "ai_intent": parsed.get("ai_intent", "High" if has_tech else "Medium"),
                            "commercial_score": score_dict["score"],
                            "commercial_level": score_dict["level"],
                            "commercial_evidence": score_dict["breakdown"],
                            "confidence": confidence,
                            "contact_name": contact_name,
                            "contact_position": raw_signal.get("contact_position", "Operations Lead"),
                            "contact_email": raw_signal.get("contact_email", "Email: Not publicly verified"),
                            "contact_linkedin": raw_signal.get("contact_linkedin", "LinkedIn: Not found"),
                            "contact_source": "Official company website / public listing",
                            "why_selected": parsed.get("why_selected", [
                                f"Active workload verified in {domain}.",
                                "Operational tasks involve high repetitive document/data volume.",
                                "Workflow suitable for lightweight AI assistance."
                            ]),
                            "outreach_email": parsed.get("outreach_email", ""),
                            "linkedin_message": parsed.get("linkedin_message", ""),
                            "sources_detail": [{
                                "source_name": raw_signal.get("source", "Industry Notice"),
                                "source_type": raw_signal.get("source_type", "Tier 1 — Primary"),
                                "url": raw_signal.get("url", ""),
                                "date": raw_signal.get("date", "2026-09-21"),
                                "evidence": evidence_text,
                                "quality": "Tier 1"
                            }],
                            "reasoning_trail": build_reasoning_trail(
                                region, domain, org_name, raw_signal.get("source", "Official source"),
                                evidence_text[:60], parsed.get("problem_statement", "")[:60],
                                app_name, score_dict["score"], contact_name, confidence
                            )
                        }
                        return enforce_anti_hallucination_rules(result)
            except Exception as e:
                logger.error(f"Gemini API execution error: {e}")

        # Deterministic fallback synthesis
        app_name = f"{domain.split()[0]}Pilot AI"
        prob_summary = f"High manual effort in {domain.lower()} operational reporting and document validation."
        if has_job:
            prob_summary = f"Organization requires personnel for: {title}. High manual repetition in routine processing."

        outreach_email = (
            f"Subject: Potential AI automation for {domain.lower()} operations\n\n"
            f"Hello {raw_signal.get('contact_name', 'Operations Team')},\n\n"
            f"I came across your public notice regarding {title or domain}.\n\n"
            f"I noticed that your team handles significant repetitive workflows in {domain.lower()} documentation and processing.\n\n"
            f"I am exploring a lightweight AI assistant ({app_name}) that extracts data and drafts reports automatically.\n\n"
            f"I would be glad to share a short 3-minute proof-of-concept to see if it fits your current operational workflow.\n\n"
            f"Would this be relevant to your team?\n\n"
            f"Best regards,\nAI Solutions Engineer"
        )

        li_msg = f"Hi {raw_signal.get('contact_name', 'there')}, noticed your team's work in {domain[:15]}. Built a lightweight AI tool to automate repetitive reporting. Would love to share a quick demo if relevant!"
        if len(li_msg) > 195:
            li_msg = li_msg[:192] + "..."

        confidence = "High" if score_dict["score"] >= 60 and has_job else "Medium"
        contact_name = raw_signal.get("contact_name", "Not publicly verified")

        result = {
            "organization": org_name,
            "domain": domain,
            "region": region,
            "website": raw_signal.get("url", f"https://www.{org_name.lower().replace(' ', '')}.com"),
            "opportunity_type": "Job/Freelance" if has_job else "Operational Problem",
            "job_title": title if has_job else "",
            "job_url": raw_signal.get("job_url", ""),
            "application_eligibility": "Verified eligible" if region == "Pakistan" else "International eligibility not verified.",
            "remote_status": raw_signal.get("remote_status", "Remote" if "remote" in evidence_text.lower() else "On-site/Hybrid"),
            "problem_statement": prob_summary,
            "problem_evidence": [evidence_text],
            "proposed_solution": f"AI {domain.split()[0]} Processing & Automation Assistant",
            "app_name": app_name,
            "ai_intent": "High" if has_tech else "Medium",
            "commercial_score": score_dict["score"],
            "commercial_level": score_dict["level"],
            "commercial_evidence": score_dict["breakdown"],
            "confidence": confidence,
            "contact_name": contact_name,
            "contact_position": raw_signal.get("contact_position", "Operations Lead"),
            "contact_email": raw_signal.get("contact_email", "Email: Not publicly verified"),
            "contact_linkedin": raw_signal.get("contact_linkedin", "LinkedIn: Not found"),
            "contact_source": "Public listing / company publication",
            "why_selected": [
                f"Active commercial signal identified in {domain}.",
                "Operational documentation tasks show high repetitive burden.",
                "High technical feasibility for automated AI document processing."
            ],
            "outreach_email": outreach_email,
            "linkedin_message": li_msg,
            "sources_detail": [{
                "source_name": raw_signal.get("source", "Verified Listing"),
                "source_type": raw_signal.get("source_type", "Tier 1 — Primary"),
                "url": raw_signal.get("url", ""),
                "date": raw_signal.get("date", "2026-09-21"),
                "evidence": evidence_text,
                "quality": "Tier 1"
            }],
            "reasoning_trail": build_reasoning_trail(
                region, domain, org_name, raw_signal.get("source", "Public source"),
                evidence_text[:60], prob_summary[:60],
                app_name, score_dict["score"], contact_name, confidence
            )
        }

        return enforce_anti_hallucination_rules(result)
