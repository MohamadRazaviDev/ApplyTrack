import { Dialog, Transition } from '@headlessui/react';
import { Fragment, useState } from 'react';
import { api } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

export default function NewApplicationModal({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    url: '',
    company_name: '',
    title: '',
    description: '',
    notes: '',
  });
  
  const queryClient = useQueryClient();
  const router = useRouter();

  const createJobMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      // 1. Create Job Posting
      const jobRes = await api.post('/job-postings', {
        url: data.url,
        title: data.title,
        description: data.description,
        company_name: data.company_name
      });
      const jobId = jobRes.data.id;

      // 2. Create Application
      const appRes = await api.post('/applications', {
        job_posting_id: jobId,
        status: 'draft',
        notes: data.notes
      });
      return appRes.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      onClose();
      setStep(1);
      setFormData({ url: '', company_name: '', title: '', description: '', notes: '' });
      // Redirect to detail page with AI prompt
      router.push(`/applications/${data.id}?new=true`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (step === 1) {
      setStep(2);
    } else {
      createJobMutation.mutate(formData);
    }
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900 mb-4">
                  Add Application (Step {step}/2)
                </Dialog.Title>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  {step === 1 ? (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Job URL</label>
                        <input 
                          type="url" required 
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                          value={formData.url}
                          onChange={e => setFormData({...formData, url: e.target.value})}
                          placeholder="https://linkedin.com/jobs/..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Company Name</label>
                        <input 
                          type="text" 
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                          value={formData.company_name}
                          onChange={e => setFormData({...formData, company_name: e.target.value})}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Role Title</label>
                        <input 
                          type="text" required 
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                          value={formData.title}
                          onChange={e => setFormData({...formData, title: e.target.value})}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Job Description</label>
                        <textarea 
                          rows={6}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                          value={formData.description}
                          onChange={e => setFormData({...formData, description: e.target.value})}
                          placeholder="Paste full JD here..."
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
                        <textarea 
                          rows={2}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2"
                          value={formData.notes}
                          onChange={e => setFormData({...formData, notes: e.target.value})}
                        />
                      </div>
                    </>
                  )}

                  <div className="mt-4 flex justify-between">
                    {step === 2 && (
                      <button
                        type="button"
                        className="inline-flex justify-center rounded-md border border-transparent bg-gray-100 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-200"
                        onClick={() => setStep(1)}
                      >
                        Back
                      </button>
                    )}
                    <div className="flex-1"></div>
                    <button
                      type="submit"
                      disabled={createJobMutation.isPending}
                      className="inline-flex justify-center rounded-md border border-transparent bg-blue-100 px-4 py-2 text-sm font-medium text-blue-900 hover:bg-blue-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                    >
                      {step === 1 ? 'Next' : (createJobMutation.isPending ? 'Creating...' : 'Create Application')}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
