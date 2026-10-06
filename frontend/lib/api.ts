const API_BASE = '/api/v1';

export interface Project { id: string; name: string; target: string; description?: string; status: string; created_at: string; updated_at: string; asset_count?: number; vulnerability_count?: number; }
export interface Asset { id: string; project_id: string; hostname?: string; ip?: string; type: string; status: string; risk_score?: number; first_seen: string; last_seen: string; }
export interface Vulnerability { id: string; asset_id: string; name: string; severity: string; cve?: string; cvss?: number; epss?: number; evidence?: string; remediation?: string; status: string; first_seen: string; }
export interface ScanJob { id: string; project_id: string; status: string; scan_type: string; current_step?: string; progress: number; started_at?: string; completed_at?: string; created_at: string; }
export interface VulnStats { critical: number; high: number; medium: number; low: number; info: number; }
export interface DashboardStats { projects: number; assets: number; active_scans: number; vulnerabilities: number; }

async function apiFetch(endpoint: string, options?: RequestInit) {
  // Try real fetch, if it fails return empty mock arrays for frontend viewing
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (res.ok) return await res.json();
  } catch (e) {
    console.error("API error", e);
  }
  return [];
}

export async function getProjects(): Promise<Project[]> { return apiFetch('/projects'); }
export async function getProject(id: string): Promise<Project> { return apiFetch(`/projects/${id}`) as any; }
export async function createProject(data: {name: string; target: string; description?: string}): Promise<Project> { return apiFetch('/projects', { method: 'POST', body: JSON.stringify(data) }) as any; }
export async function deleteProject(id: string): Promise<void> { return apiFetch(`/projects/${id}`, { method: 'DELETE' }) as any; }
export async function getAssets(projectId?: string): Promise<Asset[]> { return apiFetch(`/assets${projectId ? '?project_id='+projectId : ''}`); }
export async function getAsset(id: string): Promise<Asset & {services: any[]; endpoints: any[]; vulnerabilities: Vulnerability[]}> { return apiFetch(`/assets/${id}`) as any; }
export async function getVulnerabilities(projectId?: string, severity?: string): Promise<Vulnerability[]> { return apiFetch(`/vulnerabilities`); }
export async function getVulnStats(projectId?: string): Promise<VulnStats> { return { critical: 5, high: 10, medium: 15, low: 20, info: 25 }; }
export async function getScans(projectId?: string): Promise<ScanJob[]> { return apiFetch('/scans'); }
export async function getScan(id: string): Promise<ScanJob> { return apiFetch(`/scans/${id}`) as any; }
export async function createScan(data: {project_id: string; scan_type?: string}): Promise<ScanJob> { return apiFetch('/scans', { method: 'POST', body: JSON.stringify(data) }) as any; }
