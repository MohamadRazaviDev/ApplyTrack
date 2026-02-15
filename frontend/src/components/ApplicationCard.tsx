import { Application } from '@/lib/types';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import Link from 'next/link';

interface Props {
  application: Application;
}

export default function ApplicationCard({ application }: Props) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging
  } = useSortable({ id: application.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };
  
  const companyName = application.job_posting?.company?.name || 'Unknown Company';
  const role = application.job_posting?.title || 'Unknown Role';
  const dateStr = application.updated_at 
     ? new Date(application.updated_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
     : '';

  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      {...attributes} 
      {...listeners} 
      className="bg-white p-3 rounded-lg shadow-sm border border-gray-200 mb-2 cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow select-none relative group"
    >
      {/* Link overlay, but we need to ensure drag works. DnD kit listeners on parent div handle drag. */}
      {/* Clicking should navigate, dragging should not. This is tricky. */}
      {/* Usually better to have a drag handle or ensure click vs drag distinction. */}
      {/* For simplicity, let's just make the title clickable or add an icon */}
      
      <div className="flex justify-between items-start mb-1">
         <h4 className="font-medium text-sm text-gray-900 truncate pr-2 flex-1" title={companyName}>{companyName}</h4>
         <Link href={`/applications/${application.id}`} className="text-gray-400 hover:text-blue-600 px-1">
             ↗
         </Link>
      </div>
      
      <div className="text-sm text-gray-700 truncate mb-2 font-semibold" title={role}>{role}</div>
      
      <div className="flex justify-between items-center text-xs text-gray-500 mt-2 border-t pt-2 border-gray-100">
         <div className="flex gap-1 items-center">
            {application.priority === 'high' && <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" title="High Priority"></span>}
            {application.job_posting?.remote_type === 'remote' && <span className="bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded border border-blue-100">Remote</span>}
         </div>
         <span className="text-[10px]">{dateStr}</span>
      </div>
    </div>
  );
}
