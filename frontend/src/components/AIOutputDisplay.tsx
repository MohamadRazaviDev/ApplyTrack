import {
    ParsedJD,
    MatchResult,
    TailoredCV,
    OutreachResult,
    InterviewPrepResult,
    SkillItem,
    MatchItem,
    CVBullet,
    StoryItem,
} from '@/lib/types';
import { CheckCircle, AlertTriangle, Copy } from 'lucide-react';
import { useState } from 'react';

function EvidenceTag({ source, text }: { source: string; text: string }) {
    return (
        <span className="inline-block text-[10px] bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded mt-0.5" title={text}>
            📄 {source}
        </span>
    );
}

function CopyButton({ text }: { text: string }) {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
    };
    return (
        <button
            onClick={handleCopy}
            className="text-[var(--fg-muted)] hover:text-[var(--accent)] transition-colors"
            title="Copy to clipboard"
        >
            {copied ? <CheckCircle size={14} className="text-emerald-500" /> : <Copy size={14} />}
        </button>
    );
}

function ParseJDDisplay({ data }: { data: ParsedJD }) {
    return (
        <div className="space-y-4 text-sm">
            <div>
                <h4 className="font-bold text-base">{data.role_title}</h4>
                {data.seniority && <span className="badge bg-indigo-50 text-indigo-600 border-indigo-100">{data.seniority}</span>}
            </div>
            <div>
                <h5 className="font-semibold text-emerald-700 mb-1">Must Have</h5>
                <ul className="space-y-1">
                    {data.must_have_skills.map((s: SkillItem, i: number) => (
                        <li key={i} className="flex items-start gap-1.5">
                            <CheckCircle size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                            <div>
                                <span>{s.name}</span>
                                {s.evidence && <EvidenceTag source={s.evidence.source} text={s.evidence.text} />}
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
            <div>
                <h5 className="font-semibold text-blue-700 mb-1">Nice to Have</h5>
                <ul className="space-y-1">
                    {data.nice_to_have_skills.map((s: SkillItem, i: number) => (
                        <li key={i} className="flex items-start gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0" />
                            <span>{s.name}</span>
                        </li>
                    ))}
                </ul>
            </div>
            {data.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1">
                    {data.keywords.map((kw, i) => (
                        <span key={i} className="badge bg-slate-100 text-slate-600 border-slate-200">{kw}</span>
                    ))}
                </div>
            )}
        </div>
    );
}

function MatchDisplay({ data }: { data: MatchResult }) {
    const scoreColor =
        data.match_score >= 75 ? 'text-emerald-600' : data.match_score >= 50 ? 'text-amber-600' : 'text-red-600';
    const barColor =
        data.match_score >= 75 ? 'bg-emerald-500' : data.match_score >= 50 ? 'bg-amber-500' : 'bg-red-500';

    return (
        <div className="space-y-4 text-sm">
            <div className="flex items-center gap-3">
                <span className={`text-2xl font-bold ${scoreColor}`}>{data.match_score}%</span>
                <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className={`h-full ${barColor} transition-all`} style={{ width: `${data.match_score}%` }} />
                </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h5 className="font-semibold text-emerald-700 mb-1">Strong Matches</h5>
                    <ul className="space-y-1">
                        {data.strong_matches.map((m: MatchItem, i: number) => (
                            <li key={i} className="flex items-start gap-1.5">
                                <CheckCircle size={14} className="text-emerald-500 mt-0.5 flex-shrink-0" />
                                <span>{m.item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h5 className="font-semibold text-red-700 mb-1">Gaps</h5>
                    <ul className="space-y-1">
                        {data.gaps.map((g: MatchItem, i: number) => (
                            <li key={i} className="flex items-start gap-1.5">
                                <AlertTriangle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                                <span>{g.item}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}

function TailorCVDisplay({ data }: { data: TailoredCV }) {
    return (
        <div className="space-y-4 text-sm">
            {data.tailored_summary && (
                <div className="bg-indigo-50 p-3 rounded-lg border border-indigo-100">
                    <div className="flex items-start justify-between gap-2">
                        <p className="italic text-indigo-900">{data.tailored_summary}</p>
                        <CopyButton text={data.tailored_summary} />
                    </div>
                </div>
            )}
            <div>
                <h5 className="font-semibold mb-2">Suggested Bullets</h5>
                <ul className="space-y-2">
                    {data.bullet_suggestions.map((b: CVBullet, i: number) => (
                        <li key={i} className="bg-slate-50 p-2.5 rounded-lg border border-[var(--border)] flex items-start justify-between gap-2">
                            <span>{b.bullet}</span>
                            <CopyButton text={b.bullet} />
                        </li>
                    ))}
                </ul>
            </div>
            {data.warnings.length > 0 && (
                <div className="space-y-1">
                    {data.warnings.map((w, i) => (
                        <div key={i} className="flex items-start gap-1.5 text-amber-700">
                            <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" />
                            <span className="text-xs">{w}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function OutreachDisplay({ data }: { data: OutreachResult }) {
    return (
        <div className="space-y-4 text-sm">
            <div>
                <div className="flex items-center justify-between mb-1">
                    <h5 className="font-semibold">LinkedIn Message</h5>
                    <CopyButton text={data.linkedin_message} />
                </div>
                <div className="bg-blue-50 p-3 rounded-lg border border-blue-100 whitespace-pre-wrap text-blue-900">
                    {data.linkedin_message}
                </div>
            </div>
            <div>
                <div className="flex items-center justify-between mb-1">
                    <h5 className="font-semibold">Email</h5>
                    <CopyButton text={data.email_message} />
                </div>
                <div className="bg-slate-50 p-3 rounded-lg border border-[var(--border)] whitespace-pre-wrap">
                    {data.email_message}
                </div>
            </div>
        </div>
    );
}

function InterviewPrepDisplay({ data }: { data: InterviewPrepResult }) {
    return (
        <div className="space-y-4 text-sm">
            <div>
                <h5 className="font-semibold mb-2">Likely Questions</h5>
                <ol className="list-decimal pl-4 space-y-1">
                    {data.likely_questions.map((q, i) => (
                        <li key={i}>{q}</li>
                    ))}
                </ol>
            </div>
            <div>
                <h5 className="font-semibold mb-2">Preparation Checklist</h5>
                <ul className="space-y-1">
                    {data.checklist.map((c, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                            <CheckCircle size={14} className="text-indigo-500 mt-0.5 flex-shrink-0" />
                            <span>{c}</span>
                        </li>
                    ))}
                </ul>
            </div>
            {data.suggested_stories.length > 0 && (
                <div>
                    <h5 className="font-semibold mb-2">Suggested Stories</h5>
                    <div className="space-y-3">
                        {data.suggested_stories.map((s: StoryItem, i: number) => (
                            <div key={i} className="bg-slate-50 p-3 rounded-lg border border-[var(--border)]">
                                <p className="font-medium text-xs text-[var(--fg-muted)] mb-1">&ldquo;{s.question}&rdquo;</p>
                                <p>{s.suggested_answer}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export function AIOutputDisplay({ output }: { output: { kind: string; output_json: Record<string, unknown> } }) {
    const data = output.output_json;
    const kind = output.kind;

    if (kind === 'parse_jd') return <ParseJDDisplay data={data as unknown as ParsedJD} />;
    if (kind === 'match') return <MatchDisplay data={data as unknown as MatchResult} />;
    if (kind === 'tailor_cv') return <TailorCVDisplay data={data as unknown as TailoredCV} />;
    if (kind === 'outreach') return <OutreachDisplay data={data as unknown as OutreachResult} />;
    if (kind === 'interview_prep') return <InterviewPrepDisplay data={data as unknown as InterviewPrepResult} />;

    return <pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>;
}
