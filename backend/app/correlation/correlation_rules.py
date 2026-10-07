from abc import ABC, abstractmethod
from app.models import schema as models
from sqlalchemy.orm import Session

class CorrelationRule(ABC):
    rule_id: str
    description: str
    default_confidence: float
    
    @abstractmethod
    def evaluate(self, project_id: str, db: Session):
        pass

class AssetToFindingRule(CorrelationRule):
    rule_id = "ASSET_FINDING_LINK"
    description = "Links vulnerabilities directly to their affected asset host."
    default_confidence = 0.99
    
    def evaluate(self, project_id: str, db: Session):
        findings = db.query(models.Finding).filter_by(project_id=project_id).all()
        relations = []
        for f in findings:
            relations.append({
                "source_id": f.asset_id,
                "target_id": f.id,
                "type": "vulnerable_to",
                "confidence": self.default_confidence,
                "explanation": f"Finding '{f.title}' is linked because the normalized scanner result directly identified this asset as the affected host."
            })
        return relations

class DomainToSubdomainRule(CorrelationRule):
    rule_id = "DOMAIN_SUBDOMAIN_INFERENCE"
    description = "infers relationship between root domain and discovered subdomains."
    default_confidence = 0.85
    
    def evaluate(self, project_id: str, db: Session):
        assets = db.query(models.Asset).filter_by(project_id=project_id, asset_type="domain").all()
        relations = []
        for a1 in assets:
            for a2 in assets:
                if a1.id != a2.id and a2.value.endswith("." + a1.value):
                    relations.append({
                        "source_id": a1.id,
                        "target_id": a2.id,
                        "type": "has_subdomain",
                        "confidence": self.default_confidence,
                        "explanation": f"This relationship was inferred because '{a2.value}' is a cryptographic subdomain of '{a1.value}'."
                    })
        return relations

RULES = [AssetToFindingRule(), DomainToSubdomainRule()]
