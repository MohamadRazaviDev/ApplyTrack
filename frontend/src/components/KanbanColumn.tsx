import { Application, STATUS_META, ApplicationStatus } from '@/lib/types';
import ApplicationCard from './ApplicationCard';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

interface Props {
  id: string;
  title: string;
  applications: Application[];
}

export default function KanbanColumn({ id, title, applications }: Props) {
  const { setNodeRef, isOver } = useDroppable({ id });
  const sm = STATUS_META[id as ApplicationStatus];

  return (
    <div
      className={`rounded-xl p-3 w-72 min-w-[18rem] flex flex-col h-[calc(100vh-180px)] border transition-colors ${isOver ? 'bg-indigo-50/60 border-indigo-200' : 'bg-slate-50/80 border-[var(--border)]'
        }`}
    >
      <h3 className="font-semibold text-sm mb-3 flex items-center justify-between px-1">
        <span>{title}</span>
        <span className={`badge ${sm?.color || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
          {applications.length}
        </span>
      </h3>

      <div ref={setNodeRef} className="flex-1 overflow-y-auto pr-1">
        <SortableContext id={id} items={applications.map((a) => a.id)} strategy={verticalListSortingStrategy}>
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </SortableContext>
        {applications.length === 0 && (
          <div className="h-20 border-2 border-dashed border-[var(--border)] rounded-xl flex items-center justify-center text-xs text-[var(--fg-muted)]">
            Drop here
          </div>
        )}
      </div>
    </div>
  );
}
