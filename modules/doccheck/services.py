"""
DocCheck Module - Services/Business Logic
Enhanced with professional persona detection and tier recommendation
"""

from datetime import timedelta
from typing import Dict, List, Tuple, Any
from django.utils.timezone import now
from shared.constants.theme import DOCUMENT_TYPES, SERVICE_TIERS, SELLER_PERSONAS
from shared.utils.helpers import IDGenerator, DateUtils
from shared.exceptions import ValidationError
from .models import DocCheckSession, DocCheckResult


class DocCheckService:
    """Business logic for DocCheck assessment with persona detection"""

    @staticmethod
    def _as_bool(value: Any) -> bool:
        """Normalize truthy values coming from frontend (bools or "yes" strings)."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"yes", "true", "1"}
        return bool(value)

    # Always required documents for all sellers
    ALWAYS_REQUIRED = [
        "caderneta_predial",  # Caderneta Predial Urbana
        "certidao_permanente",  # Certidão Permanente
    ]

    @staticmethod
    def detect_persona(answers: Dict) -> Tuple[str, str]:
        """
        Detect seller persona from assessment answers.
        
        Enhanced logic: Use Q9-Q12 directly when available, fallback to Q1-Q8 logic
        
        Q9-Q12 Persona Mapping:
        - P1 (Urban): seller_residency = "portugal_resident" + straightforward answers
        - P2 (Non-Resident): seller_residency = "non_resident_eu" or "non_resident_other"
        - P3 (Heir): number_of_heirs >= "2_3" or acquisition_type = "inheritance"
        - P4 (Divorce): is_divorce_case = True OR acquisition_type = "divorce"
        - P5 (Rural): property_type = "land" OR building_construction = "pre_1951"
        
        Returns:
            (persona_slug, persona_name)
        """
        # Extract Q9-Q12 if available (new enhanced form)
        seller_residency = answers.get("seller_residency", "").lower()
        number_of_heirs = answers.get("number_of_heirs", "").lower()
        is_divorce_case = DocCheckService._as_bool(answers.get("is_divorce_case", False))
        urgency = str(answers.get("urgency", "")).lower()
        
        # Extract Q1-Q8 for fallback logic
        acquisition_type = answers.get("acquisition_type", "").lower()
        is_primary_residence = DocCheckService._as_bool(answers.get("is_primary_residence", True))
        property_type = answers.get("property_type", "").lower()
        building_age = answers.get("building_construction", "").lower()
        owners_available = answers.get("all_owners_available", "").lower()

        # Priority 1: DIVORCE (P4) - HIGHEST PRIORITY (most complex)
        # Check both Q11 (is_divorce_case) and Q5 (acquisition_type)
        if is_divorce_case or acquisition_type == "divorce":
            return ("divorce", SELLER_PERSONAS["divorce"]["name"])

        # Priority 2: RURAL (P5) - Old property or land
        if property_type == "land":
            return ("rural", SELLER_PERSONAS["rural"]["name"])
        if building_age == "pre_1951":
            return ("rural", SELLER_PERSONAS["rural"]["name"])

        # Priority 3: HEIR (P3) - Multiple owners or inheritance complexity
        # Check both Q10 (number_of_heirs) and Q5 (acquisition_type)
        if number_of_heirs in ["2_3", "4_or_more", "disputed"] or acquisition_type == "inheritance":
            if owners_available in ["one_deceased", "disputed", "one_abroad"] or number_of_heirs == "disputed":
                return ("heir", SELLER_PERSONAS["heir"]["name"])

        # Priority 4: NON-RESIDENT (P2) - Using Q9 if available, else Q6
        # Q9: seller_residency = non_resident_eu/non_resident_other
        # Q6: is_primary_residence = False (fallback)
        if seller_residency in ["non_resident_eu", "non_resident_other"]:
            return ("non_resident", SELLER_PERSONAS["non_resident"]["name"])
        if not is_primary_residence:
            return ("non_resident", SELLER_PERSONAS["non_resident"]["name"])

        # Default: URBAN RESIDENT (P1) - Portugal resident + straightforward
        # This covers: seller_residency = "portugal_resident"
        return ("urban_resident", SELLER_PERSONAS["urban_resident"]["name"])

    @staticmethod
    def calculate_missing_documents(answers: Dict) -> List[str]:
        """
        Calculate missing documents based on assessment answers.
        
        Logic:
        - Always required: caderneta_predial, certidao_permanente
        - Building post-1951: Add licenca_utilizacao
        - Building post-2004: Add ficha_tecnica_habitacao
        - No valid energy cert: Add certificado_energetico
        - Has condominium: Add declaracao_condominio
        - Has mortgage: Add distrate_hipoteca
        - Inheritance with complexity: Add habilitacao_herdeiros
        
        Returns:
            List of missing document slugs
        """
        missing = list(DocCheckService.ALWAYS_REQUIRED)
        
        building_age = answers.get("building_construction", "").lower()
        has_condominium = DocCheckService._as_bool(answers.get("has_condominium", False))
        has_energy_cert = DocCheckService._as_bool(answers.get("has_valid_energy_cert", False))
        has_mortgage = DocCheckService._as_bool(answers.get("has_mortgage", False))
        acquisition_type = answers.get("acquisition_type", "").lower()
        owners_available = answers.get("all_owners_available", "").lower()

        # Building age triggers
        if building_age in ["1951_1990", "1991_2007", "post_2007"]:
            if "licenca_utilizacao" not in missing:
                missing.append("licenca_utilizacao")

        if building_age in ["1991_2007", "post_2007"]:
            if "ficha_tecnica_habitacao" not in missing:
                missing.append("ficha_tecnica_habitacao")

        # Energy certificate
        if not has_energy_cert:
            if "certificado_energetico" not in missing:
                missing.append("certificado_energetico")

        # Condominium
        if has_condominium:
            if "declaracao_condominio" not in missing:
                missing.append("declaracao_condominio")

        # Mortgage
        if has_mortgage:
            if "distrate_hipoteca" not in missing:
                missing.append("distrate_hipoteca")

        # Inheritance with complexity
        if acquisition_type == "inheritance" and owners_available != "yes":
            if "habilitacao_herdeiros" not in missing:
                missing.append("habilitacao_herdeiros")

        return missing

    @staticmethod
    def recommend_tier(
        missing_docs: List[str],
        persona_slug: str,
        answers: Dict,
    ) -> Tuple[str, str]:
        """
        Recommend service tier based on missing documents, persona, and urgency.
        
        Tier Logic:
        - 0 missing + no risk flags → free (CTA to SmartCMA only)
        - 1-2 missing → standard (€399)
        - 3+ missing → premium (€899)
        - Acquisition = divorce → express (€1,499) [OVERRIDE]
        - Urgency = urgent|1_month|very_urgent → express [OVERRIDE]
        
        Returns:
            (tier_slug, tier_name)
        """
        # Urgency/Divorce override - always express
        acquisition_type = answers.get("acquisition_type", "").lower()
        urgency = answers.get("urgency", "").lower()
        
        # Check both old format (very_urgent) and new format (urgent, 1_month)
        is_urgent = urgency in ["urgent", "1_month", "very_urgent"]
        
        if acquisition_type == "divorce" or is_urgent:
            return ("express", SERVICE_TIERS.get("express", {}).get("name", "DocExpress"))

        # Document count logic
        num_missing = len(missing_docs)

        # No missing docs = free CTA only (no paid service)
        if num_missing == 0:
            return ("free", "Free Assessment Only")

        # 1-2 missing = Standard (€399)
        if num_missing <= 2:
            return ("standard", SERVICE_TIERS.get("standard", {}).get("name", "Standard"))

        # 3+ missing = Premium (€899)
        if num_missing >= 3:
            return ("premium", SERVICE_TIERS.get("premium", {}).get("name", "Premium"))

        # Fallback
        return ("standard", SERVICE_TIERS.get("standard", {}).get("name", "Standard"))

    @staticmethod
    def get_risk_flags(answers: Dict) -> List[Dict]:
        """
        Identify risk flags for the seller.
        
        Risk types:
        - Old property (pre-1951): May have regulatory issues
        - Low energy rating (F/G): May affect buyer financing
        - Inheritance complexity: Multiple heirs or deceased owner
        - Overseas owner: May require power of attorney
        - Disputed ownership: Legal complexity
        
        Returns:
            List of risk flag dicts with: key, message, recommendation, severity
        """
        flags = []
        building_age = answers.get("building_construction", "").lower()
        energy_class = answers.get("energy_class", "").upper()
        acquisition_type = answers.get("acquisition_type", "").lower()
        owners_available = answers.get("all_owners_available", "").lower()

        # Property age risk
        if building_age == "pre_1951":
            flags.append({
                "key": "old_property",
                "message": "Property over 70 years old - may have regulatory issues",
                "recommendation": "Recommend Simplex Safe inspection",
                "severity": "high",
            })

        # Energy class risk
        if energy_class in ["F", "G"]:
            flags.append({
                "key": "low_energy_rating",
                "message": f"Energy class {energy_class} - may affect buyer financing",
                "recommendation": "Recommend Energy Certificate update",
                "severity": "medium",
            })

        # Inheritance complexity
        if acquisition_type == "inheritance" and owners_available != "yes":
            flags.append({
                "key": "inheritance_complexity",
                "message": "Multiple heirs or legal issues - complex inheritance",
                "recommendation": "Recommend legal review and heir qualification",
                "severity": "high",
            })

        # Disputed ownership
        if owners_available == "disputed":
            flags.append({
                "key": "disputed_ownership",
                "message": "Disputed ownership - legal action required",
                "recommendation": "Require legal resolution before sale",
                "severity": "critical",
            })

        # Overseas owner
        if owners_available == "one_abroad":
            flags.append({
                "key": "overseas_owner",
                "message": "One owner abroad - may require power of attorney",
                "recommendation": "Ensure POA is valid and notarized",
                "severity": "medium",
            })

        return flags

    @staticmethod
    def build_assessment_result(email: str, answers: Dict) -> Dict:
        """
        Build complete assessment result with persona, tier, and risk flags.
        
        Returns:
            Assessment result dict with all relevant data
        """
        # Detect persona
        persona_slug, persona_name = DocCheckService.detect_persona(answers)
        
        # Calculate missing documents
        missing_docs = DocCheckService.calculate_missing_documents(answers)
        
        # Recommend tier
        tier_slug, tier_name = DocCheckService.recommend_tier(
            missing_docs,
            persona_slug,
            answers,
        )
        
        # Get risk flags
        risk_flags = DocCheckService.get_risk_flags(answers)
        
        return {
            "email": email,
            "persona": {
                "slug": persona_slug,
                "name": persona_name,
                "description": SELLER_PERSONAS.get(persona_slug, {}).get("description", ""),
                "recommended_tier": SELLER_PERSONAS.get(persona_slug, {}).get("recommended_tier", "standard"),
            },
            "missing_documents": missing_docs,
            "missing_document_count": len(missing_docs),
            "recommended_tier": {
                "slug": tier_slug,
                "name": tier_name,
                "price": SERVICE_TIERS.get(tier_slug, {}).get("price", 0) if tier_slug != "free" else 0,
            },
            "risk_flags": risk_flags,
            "has_risk_flags": len(risk_flags) > 0,
            "summary": {
                "documents_always_required": len(DocCheckService.ALWAYS_REQUIRED),
                "documents_missing_count": len(missing_docs),
                "risk_flag_count": len(risk_flags),
                "is_free_tier": tier_slug == "free",
                "is_urgent": str(answers.get("urgency", "")).lower() in ["urgent", "1_month", "very_urgent"],
            },
        }

    # Legacy methods for backward compatibility
    @staticmethod
    def start_session(email: str, property_type: str, property_location: str, is_mortgaged: bool, is_inherited: bool):
        """Create new assessment session [LEGACY]"""
        session = DocCheckSession.objects.create(
            id=IDGenerator.uuid(),
            email=email,
            property_type=property_type.lower(),
            property_location=property_location,
            is_mortgaged=is_mortgaged,
            is_inherited=is_inherited,
            seller_persona=DocCheckService._determine_persona(is_inherited, property_type),
            expires_at=now() + timedelta(hours=24),
        )
        return session

    @staticmethod
    def assess(session_id: str) -> DocCheckResult:
        """Perform assessment and generate result [LEGACY]"""
        session = DocCheckSession.objects.get(id=session_id)
        missing_docs = DocCheckService._identify_missing_documents(session)
        recommended_tier = DocCheckService._recommend_tier(session)
        total_cost, estimated_days = DocCheckService._calculate_cost_and_timeline(missing_docs, recommended_tier)
        result = DocCheckResult.objects.create(
            session=session,
            missing_documents=missing_docs,
            required_tier=recommended_tier,
            total_cost=total_cost,
            estimated_days=estimated_days,
        )
        return result

    @staticmethod
    def _identify_missing_documents(session: DocCheckSession) -> list:
        """Determine which documents are missing [LEGACY]"""
        missing = ["caderneta", "certidao", "energy_cert"]
        if session.is_mortgaged:
            missing.append("ipt")
        if session.property_type == "apartment":
            missing.append("licenca")
        return missing

    @staticmethod
    def _recommend_tier(session: DocCheckSession) -> str:
        """Recommend service tier based on session data [LEGACY]"""
        if session.is_inherited:
            return "premium"
        elif session.is_mortgaged:
            return "standard"
        else:
            return "standard"

    @staticmethod
    def _calculate_cost_and_timeline(missing_docs: list, tier: str) -> tuple:
        """Calculate total cost and estimated timeline [LEGACY]"""
        tier_data = SERVICE_TIERS.get(tier, {})
        doc_cost = sum(DOCUMENT_TYPES.get(doc, {}).get("cost", 0) for doc in missing_docs)
        total_cost = tier_data.get("price", 0) + doc_cost
        estimated_days = tier_data.get("turnaround_days", 7)
        return total_cost, estimated_days

    @staticmethod
    def _determine_persona(is_inherited: bool, property_type: str) -> str:
        """Determine seller persona [LEGACY]"""
        if is_inherited:
            return "heir"
        elif property_type == "quinta":
            return "rural"
        else:
            return "urban_resident"
