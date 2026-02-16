'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import KanbanColumn from '@/components/KanbanColumn';
import NewApplicationModal from '@/components/NewApplicationModal';
import { Application, KANBAN_COLUMNS, STATUS_META, ApplicationStatus } from '@/lib/types';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  useSensor,
  useSensors,
  PointerSensor,
  closestCorners,
} from '@dnd-kit/core';
import ApplicationCard from '@/components/ApplicationCard';
import { Plus, Search } from 'lucide-react';

export default function ApplicationsPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const { data: applications = [], isLoading } = useQuery<Application[]>({
    queryKey: ['applications'],
    queryFn: async () => (await api.get('/applications')).data,
  });

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      await api.patch(`/applications/${id}`, { status });
    },
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: ['applications'] });
      const prev = queryClient.getQueryData<Application[]>(['applications']);
      queryClient.setQueryData<Application[]>(['applications'], (old) =>
        old?.map((a) => (a.id === id ? { ...a, status: status as ApplicationStatus } : a)) || [],
      );
      return { prev };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) queryClient.setQueryData(['applications'], ctx.prev);
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: ['applications'] }),
  });

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  );

  const handleDragStart = (event: DragStartEvent) => setActiveId(event.active.id as string);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    if (!over) return;

    const draggedId = active.id as string;
    const overId = over.id as string;
    const app = applications.find((a) => a.id === draggedId);
    if (!app) return;

    let newStatus = app.status as string;
    if (KANBAN_COLUMNS.includes(overId as ApplicationStatus)) {
      newStatus = overId;
    } else {
      const overApp = applications.find((a) => a.id === overId);
      if (overApp) newStatus = overApp.status;
    }

    if (newStatus !== app.status) {
      updateStatusMutation.mutate({ id: draggedId, status: newStatus });
    }
  };

  // filter by search
  const filtered = search
    ? applications.filter((a) => {
      const q = search.toLowerCase();
      return (
        (a.job_posting?.title || '').toLowerCase().includes(q) ||
        (a.job_posting?.company?.name || '').toLowerCase().includes(q)
      );
    })
    : applications;

  const activeApp = activeId ? applications.find((a) => a.id === activeId) : null;

  if (isLoading) {
    return (
      <div className="flex gap-4 p-4 overflow-x-auto">
        {KANBAN_COLUMNS.map((col) => (
          <div key={col} className="skeleton w-72 min-w-[18rem] h-96 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-56px)] flex flex-col p-4">
      {/* toolbar */}
      <div className="flex items-center justify-between mb-4 gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--fg-muted)]" />
          <input
            type="text"
            placeholder="Search company or role…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-[var(--border)] bg-white pl-9 pr-4 py-2 text-sm focus:border-[var(--accent)] focus:ring-2 focus:ring-indigo-100 outline-none transition"
          />
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-1.5 rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--accent-hover)] transition-colors shadow-sm"
        >
          <Plus size={16} /> New Application
        </button>
      </div>

      {/* kanban board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-4 overflow-x-auto pb-4 flex-1 items-start">
          {KANBAN_COLUMNS.map((col) => (
            <KanbanColumn
              key={col}
              id={col}
              title={STATUS_META[col].label}
              applications={filtered.filter((a) => a.status === col)}
            />
          ))}
        </div>
        <DragOverlay>{activeApp ? <ApplicationCard application={activeApp} /> : null}</DragOverlay>
      </DndContext>

      <NewApplicationModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
