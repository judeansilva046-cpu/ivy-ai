'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { Zap, RefreshCw, Trash2, Loader } from 'lucide-react';

interface Workflow {
  id: string;
  name: string;
  active: boolean;
}

interface EventLog {
  id: string;
  event_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
}

export default function AutomationPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [events, setEvents] = useState<EventLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [workflowRes, eventsRes] = await Promise.all([
        apiClient.get('/n8n/workflows'),
        apiClient.get('/n8n/events?limit=20'),
      ]);

      setWorkflows(workflowRes.data.data || []);
      setEvents(eventsRes.data.events || []);
    } catch (error) {
      console.error('Error fetching automation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerWorkflow = async (workflowId: string) => {
    setTriggering(workflowId);
    try {
      await apiClient.post('/n8n/trigger', {
        workflow_id: workflowId,
        data: {
          timestamp: new Date().toISOString(),
        },
      });
      await fetchData();
    } catch (error) {
      alert('Erro ao ativar workflow');
    } finally {
      setTriggering(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400';
      case 'processing':
        return 'bg-blue-500/20 text-blue-400';
      case 'failed':
        return 'bg-red-500/20 text-red-400';
      default:
        return 'bg-yellow-500/20 text-yellow-400';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Automações N8N</h1>
        <p className="text-gray-400">Gerencie workflows e eventos</p>
      </div>

      {/* Workflows Section */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            Workflows Disponíveis
          </h2>
          <button
            onClick={fetchData}
            disabled={loading}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-400">
            <Loader className="w-5 h-5 animate-spin mx-auto mb-2" />
            Carregando...
          </div>
        ) : workflows.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>Nenhum workflow encontrado</p>
            <p className="text-sm mt-2">Configure N8N_URL no backend</p>
          </div>
        ) : (
          <div className="space-y-3">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="flex justify-between items-center p-4 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-gray-500 transition-colors"
              >
                <div>
                  <p className="text-white font-medium">{workflow.name}</p>
                  <p className="text-xs text-gray-400">{workflow.id}</p>
                </div>
                <button
                  onClick={() => handleTriggerWorkflow(workflow.id)}
                  disabled={triggering === workflow.id}
                  className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:opacity-50 text-white rounded flex items-center gap-2 transition-colors"
                >
                  {triggering === workflow.id ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      Ativando...
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      Ativar
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Events Section */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h2 className="text-xl font-bold text-white mb-6">Histórico de Eventos</h2>

        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            Nenhum evento registrado
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase">
                    Tipo
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase">
                    Status
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-gray-400 uppercase">
                    Data
                  </th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-gray-400 uppercase">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {events.map((event) => (
                  <tr key={event.id} className="hover:bg-gray-700/50">
                    <td className="px-4 py-3">
                      <span className="text-white text-sm">{event.event_type}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(event.status)}`}>
                        {event.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-gray-400 text-sm">
                        {new Date(event.created_at).toLocaleString('pt-BR')}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        className="text-red-400 hover:text-red-300 transition-colors"
                        title="Deletar evento"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
        <p className="text-blue-400 text-sm">
          💡 N8N integrado com Jarvis AI. Configure workflows em N8N e ative-os aqui.
        </p>
      </div>
    </div>
  );
}
