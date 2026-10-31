"""
risk.py — Transparent, Verifiable Risk Scoring Engine
VirgoYT OSINT Toolkit v4.0
Developer Credit: VIRGOYT707
"""

from typing import Dict, Any, List, Optional
from .config import C

class RiskEngine:
    """
    Transparent telecom risk assessment engine.
    Separates syntax/numbering validation from behavioral/fraud risk.
    Provides verifiable explanations for every scoring signal.
    """

    @staticmethod
    def evaluate(analysis: Dict[str, Any], platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate phone intelligence metadata and generate a documented risk profile.
        """
        factors: List[Dict[str, Any]] = []
        base_score = 0
        error = analysis.get("error")
        is_valid = analysis.get("is_valid", False)
        is_possible = analysis.get("is_possible", False)
        line_type = analysis.get("line_type", "Unknown Line Type")
        carrier = analysis.get("carrier", "UNKNOWN")
        country = analysis.get("country_name", "UNKNOWN")

        # ── 1. INSUFFICIENT EVIDENCE CHECK ──
        if error and not is_possible:
            return {
                "score": None,
                "score_display": "UNKNOWN",
                "risk_level": "UNKNOWN",
                "confidence": "INSUFFICIENT",
                "factors": [{
                    "code": "PARSE_FAILURE",
                    "delta": 0,
                    "category": "Validation",
                    "reason": f"Insufficient telecom data: {error}. Cannot calculate reliable risk.",
                }],
                "technical_summary": "Input failed basic ITU-T E.164 parsing.",
                "limitations": [
                    "No risk rating can be derived from malformed inputs.",
                    "Format syntax failure does not constitute proof of criminal activity.",
                ],
            }

        # ── 2. TECHNICAL VALIDATION SIGNALS ──
        if not is_valid and is_possible:
            base_score += 25
            factors.append({
                "code": "NUMBERING_PLAN_MISMATCH",
                "delta": +25,
                "category": "Technical Validation",
                "reason": "Number length is possible, but digits do not match any active national numbering plan assignment. Incoming calls bearing this ID are likely spoofed.",
            })
        elif not is_valid and not is_possible:
            base_score += 35
            factors.append({
                "code": "INVALID_NUMBER_STRUCTURE",
                "delta": +35,
                "category": "Technical Validation",
                "reason": "Number violates standard E.164 length/structure rules. If received as caller ID, high probability of telecommunication header spoofing.",
            })

        # ── 3. TELECOM INFRASTRUCTURE / ANONYMITY SIGNALS ──
        if analysis.get("is_voip") or "VoIP" in line_type:
            base_score += 35
            factors.append({
                "code": "VOIP_VIRTUAL_ALLOCATION",
                "delta": +35,
                "category": "Telecom Infrastructure",
                "reason": "VoIP / virtual telephony allows rapid online provisioning and disposal without physical SIM KYC verification. Frequently used for burner/privacy services.",
            })
        elif line_type in ("Toll-Free", "Premium Rate", "Shared Cost"):
            base_score += 20
            factors.append({
                "code": "NON_STANDARD_TARIFF",
                "delta": +20,
                "category": "Tariff / Routing",
                "reason": f"Line type is '{line_type}'. Inbound unsolicited contact claiming to originate from toll-free or premium tariffs frequently correlates with toll-fraud / wangiri scams.",
            })

        # ── 4. CARRIER REGISTRY CORRELATION ──
        if "UNAVAILABLE" in carrier or carrier in ("UNKNOWN", "", None):
            base_score += 15
            factors.append({
                "code": "CARRIER_METADATA_UNAVAILABLE",
                "delta": +15,
                "category": "Telecom Registry",
                "reason": "No registered telecommunication operator found in public ITU-T allocation tables for this prefix block.",
            })
        elif line_type == "Mobile":
            base_score -= 10
            factors.append({
                "code": "VERIFIED_MOBILE_ALLOCATION",
                "delta": -10,
                "category": "Telecom Registry",
                "reason": f"Allocated to recognized national mobile network ({carrier}) subject to standard regulatory SIM registration frameworks.",
            })
        elif line_type == "Fixed Line":
            base_score -= 5
            factors.append({
                "code": "PHYSICAL_WIRELINE_ALLOCATION",
                "delta": -5,
                "category": "Telecom Registry",
                "reason": "Allocated to a physical wireline exchange typically associated with fixed street infrastructure or enterprise premises.",
            })

        # ── 5. OPTIONAL CONTACT CONTEXT ──
        if platform:
            plat_lower = platform.lower()
            if "sms" in plat_lower or "telegram" in plat_lower or "whatsapp" in plat_lower:
                if analysis.get("is_voip"):
                    base_score += 10
                    factors.append({
                        "code": "VOIP_ON_MESSAGING_PLATFORM",
                        "delta": +10,
                        "category": "Context Correlation",
                        "reason": f"VoIP number utilized as registration identity on messaging platform '{platform}'. Heightens potential for disposable/throwaway account usage.",
                    })

        # Bound score between 0 and 100
        final_score = max(0, min(100, base_score))

        # Risk Level & Classification
        if final_score >= 70:
            risk_level = "HIGH SUSPICION"
        elif final_score >= 45:
            risk_level = "ELEVATED"
        elif final_score >= 20:
            risk_level = "GUARDED"
        else:
            risk_level = "LOW"

        # Confidence Rating
        if is_valid and "UNAVAILABLE" not in carrier and country != "UNKNOWN":
            confidence = "HIGH"
        elif is_valid:
            confidence = "MEDIUM"
        elif is_possible:
            confidence = "LOW"
        else:
            confidence = "INSUFFICIENT"

        return {
            "score": final_score,
            "score_display": f"{final_score}/100",
            "risk_level": risk_level,
            "confidence": confidence,
            "factors": factors,
            "technical_summary": "Valid numbering plan allocation" if is_valid else "Non-compliant numbering plan",
            "limitations": [
                "Score reflects technical infrastructure signals, NOT criminal conviction or certainty of fraud.",
                "Legitimate businesses and privacy-conscious users routinely utilize VoIP solutions.",
                "Caller ID spoofing can make fraudulent calls appear to originate from legitimate, low-risk numbers.",
            ],
        }

    @staticmethod
    def format_risk_bar(score: Optional[int], risk_level: str) -> str:
        """Render a color-coded ASCII assessment bar."""
        if score is None:
            return f"{C.D}[░░░░░░░░░░░░░░░░░░░░] UNKNOWN [INSUFFICIENT DATA]{C.RST}"

        filled = score // 5
        empty = 20 - filled

        if score >= 70:
            color = C.R
        elif score >= 45:
            color = C.Y
        elif score >= 20:
            color = C.CN
        else:
            color = C.G

        bar = f"{color}{'█' * filled}{'░' * empty}{C.RST}"
        return f"{bar} {color}{score}/100 [{risk_level}]{C.RST}"
