export interface Company {
  id: string;
  name: string;
  website_url?: string;
}

export interface JobPosting {
  id: string;
  title: string;
  company_id?: string;
  location?: string;
  remote_type: string;
  posting_url?: string;
  source: string;
  description_raw?: string;
  created_at: string;
  company?: Company;
}

export interface Application {
  id: string;
  user_id: string;
  job_posting_id: string;
  status: string;
  priority: string;
  notes: string;
  applied_at?: string;
  next_followup_at?: string;
  salary_expectation?: number;
  created_at: string;
  updated_at: string;
  job_posting?: JobPosting;
}

export interface AIOutput {
  id: string;
  kind: string;
  output_json: any;
  created_at: string;
}
