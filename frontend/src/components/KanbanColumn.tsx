import { Application } from '@/lib/types';
import ApplicationCard from './ApplicationCard';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';

interface Props {
  id: string;
  title: string;
  applications: Application[];
}

export default function KanbanColumn({ id, title, applications }: Props) {
  const { setNodeRef } = useDroppable({ id });

  return (
    <div className="bg-gray-50 rounded-lg p-3 w-72 flex flex-col h-[calc(100vh-200px)] border border-gray-200">
      <h3 className="font-semibold text-gray-700 mb-3 text-sm flex justify-between items-center">
        {title} 
        <span className="bg-gray-200 text-gray-600 px-2 rounded-full text-xs py-0.5">{applications.length}</span>
      </h3>
      
      <div ref={setNodeRef} className="flex-1 overflow-y-auto pr-1">
        <SortableContext 
            id={id}
            items={applications.map(app => app.id)} 
            strategy={verticalListSortingStrategy}
        >
          {applications.map((app) => (
            <ApplicationCard key={app.id} application={app} />
          ))}
        </SortableContext>
        {applications.length === 0 && (
            <div className="h-24 border-2 border-dashed border-gray-200 rounded flex items-center justify-center text-gray-400 text-xs text-center p-2">
            Empty
            </div>
        )}
      </div>
    </div>
  );
}
