/* ── types matching the rewritten backend schemas ── */

export type ApplicationStatus =
  | 'not_applied'
  | 'applied'
  | 'interview'
  | 'offer'
  | 'rejected'
  | 'archived';

export type ApplicationPriority = 'low' | 'medium' | 'high';

export type AIOutputKind =
  | 'parse_jd'
  | 'match'
  | 'tailor_cv'
  | 'outreach'
  | 'interview_prep';

export interface Company {
  id: string;
  name: string;
  website_url?: string;
  hq_location?: string;
  created_at: string;
}

export interface JobPosting {
  id: string;
  title: string;
  company_id?: string;
  location?: string;
  remote_type: 'onsite' | 'hybrid' | 'remote';
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
  status: ApplicationStatus;
  priority: ApplicationPriority;
  notes: string;
  applied_at?: string;
  next_followup_at?: string;
  salary_expectation?: number;
  created_at: string;
  updated_at: string;
  job_posting?: JobPosting;
}

export interface Reminder {
  id: string;
  application_id: string;
  user_id: string;
  text: string;
  due_at: string;
  done: boolean;
  created_at: string;
}

export interface EvidenceSnippet {
  source: string;
  text: string;
}

export interface SkillItem {
  name: string;
  evidence?: EvidenceSnippet;
}

export interface MatchItem {
  item: string;
  evidence?: EvidenceSnippet;
}

export interface CVBullet {
  bullet: string;
  evidence?: EvidenceSnippet;
}

export interface StoryItem {
  question: string;
  suggested_answer: string;
  evidence?: EvidenceSnippet;
}

export interface ParsedJD {
  role_title: string;
  seniority?: string;
  must_have_skills: SkillItem[];
  nice_to_have_skills: SkillItem[];
  responsibilities: string[];
  keywords: string[];
  questions_to_ask: string[];
}

export interface MatchResult {
  match_score: number;
  strong_matches: MatchItem[];
  gaps: MatchItem[];
  recommended_projects: string[];
  recommended_experience: string[];
}

export interface TailoredCV {
  tailored_summary: string;
  bullet_suggestions: CVBullet[];
  top_keywords: string[];
  warnings: string[];
}

export interface OutreachResult {
  linkedin_message: string;
  email_message: string;
}

export interface InterviewPrepResult {
  likely_questions: string[];
  checklist: string[];
  suggested_stories: StoryItem[];
}

export interface AIOutput {
  id: string;
  kind: AIOutputKind;
  output_json: Record<string, unknown>;
  evidence_json?: Record<string, unknown>;
  model: string;
  latency_seconds: number;
  created_at: string;
}

export interface AITaskResponse {
  task_id: string;
  status: string;
}

export interface AITaskStatusResponse {
  task_id: string;
  status: string;
  result?: Record<string, unknown>;
}

export const STATUS_META: Record<ApplicationStatus, { label: string; color: string }> = {
  not_applied: { label: 'Not Applied', color: 'bg-slate-100 text-slate-700 border-slate-200' },
  applied: { label: 'Applied', color: 'bg-blue-100 text-blue-700 border-blue-200' },
  interview: { label: 'Interview', color: 'bg-violet-100 text-violet-700 border-violet-200' },
  offer: { label: 'Offer', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700 border-red-200' },
  archived: { label: 'Archived', color: 'bg-gray-100 text-gray-500 border-gray-200' },
};

export const KANBAN_COLUMNS: ApplicationStatus[] = [
  'not_applied',
  'applied',
  'interview',
  'offer',
  'rejected',
  'archived',
];
