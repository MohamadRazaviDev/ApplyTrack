import { Application } from '@/lib/types';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import Link from 'next/link';
import { ExternalLink } from 'lucide-react';

interface Props {
  application: Application;
}

const PRIORITY_DOT: Record<string, string> = {
  high: 'bg-red-500',
  medium: 'bg-amber-400',
  low: 'bg-emerald-400',
};

export default function ApplicationCard({ application }: Props) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: application.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const company = application.job_posting?.company?.name || 'Unknown';
  const role = application.job_posting?.title || 'Unknown Role';
  const dateStr = application.updated_at
    ? new Date(application.updated_at).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    })
    : '';

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="kanban-card bg-white p-3 rounded-xl border border-[var(--border)] mb-2 cursor-grab active:cursor-grabbing select-none group"
    >
      <div className="flex items-start justify-between gap-1 mb-1">
        <h4 className="font-semibold text-sm truncate flex-1" title={company}>
          {company}
        </h4>
        <Link
          href={`/applications/${application.id}`}
          onClick={(e) => e.stopPropagation()}
          className="text-[var(--fg-muted)] hover:text-[var(--accent)] opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <ExternalLink size={14} />
        </Link>
      </div>

      <div className="text-sm text-[var(--fg-muted)] truncate mb-2" title={role}>
        {role}
      </div>

      <div className="flex items-center justify-between text-xs mt-2 pt-2 border-t border-[var(--border)]">
        <div className="flex items-center gap-1.5">
          <span
            className={`w-2 h-2 rounded-full ${PRIORITY_DOT[application.priority] || PRIORITY_DOT.medium}`}
            title={`${application.priority} priority`}
          />
          {application.job_posting?.remote_type === 'remote' && (
            <span className="badge bg-blue-50 text-blue-600 border-blue-100 !text-[10px] !py-0">
              Remote
            </span>
          )}
        </div>
        <span className="text-[10px] text-[var(--fg-muted)]">{dateStr}</span>
      </div>
    </div>
  );
}
