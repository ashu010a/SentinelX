from sqlalchemy.orm import Session
from app.models import schema as models
from .correlation_models import SecurityGraph, GraphNode, GraphEdge, RiskPath

def get_project_graph(project_id: str, db: Session) -> SecurityGraph:
    assets = db.query(models.Asset).filter_by(project_id=project_id).all()
    findings = db.query(models.Finding).filter_by(project_id=project_id).all()
    rels = db.query(models.Relationship).filter_by(project_id=project_id).all()
    
    nodes = []
    for a in assets:
        nodes.append(GraphNode(id=a.id, type="asset", label=a.value))
    for f in findings:
        nodes.append(GraphNode(id=f.id, type="finding", label=f.title, severity=f.severity))
        
    edges = []
    for r in rels:
        edges.append(GraphEdge(
            id=r.id, source=r.source_id, target=r.target_id, type=r.relationship_type,
            confidence=r.confidence, explanation=r.explanation
        ))
        
    return SecurityGraph(nodes=nodes, edges=edges)

def calculate_risk_paths(project_id: str, db: Session):
    graph = get_project_graph(project_id, db)
    paths = []
    
    # Simple traversal: Internet -> Asset -> Finding
    for edge in graph.edges:
        if edge.type == "vulnerable_to":
            asset = next((n for n in graph.nodes if n.id == edge.source), None)
            finding = next((n for n in graph.nodes if n.id == edge.target), None)
            if asset and finding:
                # Mock risk pull
                risk = db.query(models.RiskScore).filter_by(asset_id=asset.id).first()
                score = risk.score if risk else 5.0
                
                internet_node = GraphNode(id="INTERNET", type="external", label="Internet")
                exposure_edge = GraphEdge(
                    id=f"exp_{asset.id}", source="INTERNET", target=asset.id, 
                    type="exposes", confidence=1.0, explanation="Asset is publicly routable."
                )
                
                paths.append(RiskPath(
                    id=f"path_{edge.id}",
                    nodes=[internet_node, asset, finding],
                    edges=[exposure_edge, edge],
                    path_risk=score,
                    highest_risk_finding=finding.label,
                    explanation=f"Internet exposed asset '{asset.label}' contains vulnerability '{finding.label}'. Overall path risk is {score}."
                ))
    # Sort by risk descending
    paths.sort(key=lambda x: x.path_risk, reverse=True)
    return paths
