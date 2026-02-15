'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import KanbanColumn from '@/components/KanbanColumn';
import NewApplicationModal from '@/components/NewApplicationModal';
import { Application } from '@/lib/types';
import { 
  DndContext, 
  DragEndEvent, 
  DragOverlay, 
  DragStartEvent, 
  useSensor, 
  useSensors, 
  PointerSensor,
  closestCorners
} from '@dnd-kit/core';
import ApplicationCard from '@/components/ApplicationCard';

// Define status columns (IDs must match ApplicationStatus enum)
const STATUSES = [
  { id: 'draft', title: 'Draft' },
  { id: 'applied', title: 'Applied' },
  { id: 'hr_screen', title: 'HR Screen' },
  { id: 'tech_screen', title: 'Tech Screen' },
  { id: 'rejected', title: 'Rejected' },
];

export default function ApplicationsPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);

  const { data: applications = [], isLoading } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: async () => {
      const res = await api.get('/applications');
      return res.data;
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string, status: string }) => {
      await api.post(`/applications/${id}/status`, { status }); // Actually backend implementation might differ
      // The previous implementation used PATCH /applications/{id}
      await api.patch(`/applications/${id}`, { status });
    },
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['applications'] });
      const previousApps = queryClient.getQueryData<Application[]>(['applications']);

      queryClient.setQueryData<Application[]>(['applications'], (old) => {
        return old?.map(app => app.id === id ? { ...app, status } : app) || [];
      });

      return { previousApps };
    },
    onError: (err, newApp, context) => {
      if (context?.previousApps) {
        queryClient.setQueryData(['applications'], context.previousApps);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    const activeId = active.id as string;
    setActiveId(null);

    if (!over) return;

    const overId = over.id as string;
    
    // Find dragged app
    const app = applications.find(a => a.id === activeId);
    if (!app) return;

    let newStatus = app.status;

    // Check if dropped on a column container (droppable id = status)
    if (STATUSES.some(s => s.id === overId)) {
        newStatus = overId;
    } else {
        // Dropped on another item? find its status
        const overApp = applications.find(a => a.id === overId);
        if (overApp) {
            newStatus = overApp.status;
        }
    }

    if (newStatus !== app.status) {
        updateStatusMutation.mutate({ id: activeId, status: newStatus });
    }
  };

  const activeApp = activeId ? applications.find(a => a.id === activeId) : null;

  if (isLoading) return <div className="p-8">Loading applications...</div>;

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Applications Board</h1>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-medium shadow-sm transition-colors"
        >
          + New Application
        </button>
      </div>

      <DndContext 
        sensors={sensors} 
        collisionDetection={closestCorners}
        onDragStart={handleDragStart} 
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4 h-full items-start">
          {STATUSES.map(col => (
            <KanbanColumn
              key={col.id}
              id={col.id}
              title={col.title}
              applications={applications.filter(app => app.status === col.id)}
            />
          ))}
        </div>
        <DragOverlay>
            {activeApp ? <ApplicationCard application={activeApp} /> : null}
        </DragOverlay>
      </DndContext>

      <NewApplicationModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
