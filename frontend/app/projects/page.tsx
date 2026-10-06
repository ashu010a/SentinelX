'use client';
import { useState, useEffect } from 'react';
import { getProjects, createProject, createScan, Project } from '@/lib/api';
import Button from '@/components/ui/Button';
import Modal from '@/components/ui/Modal';
import Card from '@/components/ui/Card';

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Form state
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [scanLoading, setScanLoading] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await getProjects();
      setProjects(data || []);
    } catch(e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createProject({ name, target, description });
      setIsModalOpen(false);
      setName('');
      setTarget('');
      setDescription('');
      loadProjects();
    } catch (e) {
      console.error(e);
    }
    setSubmitting(false);
  };

  const handleStartScan = async (projectId: string) => {
    setScanLoading(projectId);
    try {
      await createScan({ project_id: projectId });
      alert('Scan triggered! Check the Dashboard or Assets pages in a few seconds to see the results.');
    } catch (e) {
      console.error(e);
    }
    setScanLoading(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Projects</h1>
        <Button onClick={() => setIsModalOpen(true)}>New Project</Button>
      </div>

      {loading ? (
        <div className="animate-pulse grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
           <div className="h-40 bg-[#111118] border border-[#1e1e2e] rounded-xl"></div>
           <div className="h-40 bg-[#111118] border border-[#1e1e2e] rounded-xl"></div>
        </div>
      ) : projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-[#1e1e2e] rounded-xl">
          <h3 className="text-lg font-medium text-white">No projects yet</h3>
          <p className="mt-2 text-sm text-gray-400 max-w-sm">Create your first project to start scanning domains and IPs.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(p => (
            <Card key={p.id} title={p.name}>
              <div className="text-sm text-gray-300 mb-4 truncate font-mono bg-[#0a0a0f] p-2 rounded border border-[#1e1e2e]">
                {p.target}
              </div>
              <div className="text-sm text-gray-400 mb-6 h-10 overflow-hidden text-ellipsis">
                {p.description || 'No description provided.'}
              </div>
              <div className="flex justify-end pt-4 border-t border-[#1e1e2e]">
                <Button 
                  size="sm" 
                  isLoading={scanLoading === p.id} 
                  onClick={() => handleStartScan(p.id)}
                >
                  Start Scan
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Project">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Name</label>
            <input required type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-md px-3 py-2 text-white focus:outline-none focus:border-[#6366f1]" placeholder="e.g. My Website" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Target URL/IP</label>
            <input required type="text" value={target} onChange={e => setTarget(e.target.value)} className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-md px-3 py-2 text-white focus:outline-none focus:border-[#6366f1]" placeholder="e.g. example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
            <textarea value={description} onChange={e => setDescription(e.target.value)} className="w-full bg-[#0a0a0f] border border-[#1e1e2e] rounded-md px-3 py-2 text-white focus:outline-none focus:border-[#6366f1]" rows={3} placeholder="Optional notes..."></textarea>
          </div>
          <div className="flex justify-end pt-4 space-x-3">
            <Button variant="secondary" onClick={() => setIsModalOpen(false)} type="button">Cancel</Button>
            <Button type="submit" isLoading={submitting}>Create</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
