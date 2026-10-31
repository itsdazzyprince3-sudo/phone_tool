"""
spiderfoot.py — SpiderFoot OSINT Modules & Correlation Engine
VirgoYT OSINT Toolkit v5.0
Developer Credit: VIRGOYT707
"""

from typing import Dict, Any, List
import urllib.parse
from .config import C

class SpiderFootEngine:
    """
    SpiderFoot-inspired OSINT correlation and module targeting engine.
    Maps phone indicators to automated target entity correlations.
    """

    SUPPORTED_MODULES = [
        {
            "id": "sfp_numverify",
            "name": "NumVerify Lookup",
            "cat": "Carrier & Validation",
            "desc": "Validates national prefix, carrier assignment, and line classification.",
            "target": "PHONE_NUMBER"
        },
        {
            "id": "sfp_hunter",
            "name": "Hunter.io & Email Intersect",
            "cat": "Identity Correlation",
            "desc": "Correlates phone metadata with associated corporate domain emails.",
            "target": "EMAILADDR"
        },
        {
            "id": "sfp_haveibeenpwned",
            "name": "HIBP / Breach Dumps",
            "cat": "Leaked Credentials",
            "desc": "Cross-references breach listings for records containing phone/identity pairs.",
            "target": "LEAKSITE_CONTENT"
        },
        {
            "id": "sfp_intelx",
            "name": "Intelligence X Archive",
            "cat": "Deep / Darknet Recon",
            "desc": "Scans historical paste dumps, darknet leaks, and exposed archives.",
            "target": "DARKNET_MENTION"
        },
        {
            "id": "sfp_sociallinks",
            "name": "Social Media Footprinter",
            "cat": "Social Footprint",
            "desc": "Probes registration endpoints across 50+ global social networks.",
            "target": "ACCOUNT_EXTERNAL_OWNED"
        },
        {
            "id": "sfp_whois",
            "name": "Domain WHOIS Registrar Intersect",
            "cat": "Infrastructure",
            "desc": "Detects domains registered with this technical or admin contact number.",
            "target": "DOMAIN_NAME"
        },
    ]

    @classmethod
    def list_modules(cls) -> List[Dict[str, str]]:
        return cls.SUPPORTED_MODULES

    @classmethod
    def generate_targets(cls, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert telecom intelligence into SpiderFoot-compatible entity targets."""
        e164 = analysis.get("e164", "")
        intl = analysis.get("international", "")
        nat = analysis.get("national", "")
        raw_nat = analysis.get("formats", {}).get("raw_national", "")

        targets = {
            "PHONE_NUMBER": [t for t in [e164, intl, nat, raw_nat] if t],
            "SIMULATED_MODULES": cls.SUPPORTED_MODULES,
            "CORRELATED_QUERIES": []
        }

        if e164:
            enc = urllib.parse.quote_plus(e164)
            targets["CORRELATED_QUERIES"] = [
                {"module": "sfp_intelx", "query": f"https://intelx.io/?s={enc}"},
                {"module": "sfp_whois", "query": f"https://viewdns.info/whois/?domain={enc}"},
                {"module": "sfp_haveibeenpwned", "query": f"https://haveibeenpwned.com/unifiedsearch/{enc}"},
                {"module": "sfp_numverify", "query": f"https://numverify.com"},
            ]

        return targets

    @classmethod
    def format_spiderfoot_summary(cls, sf_data: Dict[str, Any]) -> List[str]:
        """Format an aligned console representation of the SpiderFoot scans."""
        lines = []
        modules = sf_data.get("SIMULATED_MODULES", [])
        queries = sf_data.get("CORRELATED_QUERIES", [])

        lines.append(f"  {C.R}║{C.RST}  {C.DC}┌── SPIDERFOOT OSINT MODULE CORRELATIONS ────────────────{C.RST}   {C.R}║{C.RST}")
        lines.append(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🕷️  {C.W}Active Modules Loaded:{C.RST} {C.G}{len(modules)}{C.RST}")

        for mod in modules:
            lines.append(
                f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.CN}[{mod['id']}]{C.RST} {C.W}{mod['name']:<28}{C.RST} "
                f"{C.D}▸ {mod['cat']}{C.RST}"
            )

        if queries:
            lines.append(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")
            lines.append(f"  {C.R}║{C.RST}  {C.DC}│{C.RST} 🎯 {C.W}SpiderFoot Target Integrations:{C.RST}")
            for q in queries:
                lines.append(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}   {C.DG}▸{C.RST} {C.D}{q['module']:<18}:{C.RST} {C.CN}{q['query']}{C.RST}")

        lines.append(f"  {C.R}║{C.RST}  {C.DC}│{C.RST}")
        return lines
