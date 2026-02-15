interface ParsedJD {
    title: string;
    must_have_skills: string[];
    nice_to_have_skills: string[];
    responsibilities: string[];
}

interface MatchResult {
    match_score: number;
    strong_matches: { item: string }[];
    missing_skills: { item: string }[];
    tailored_angle: string;
}

interface TailoredCV {
    bullet_suggestions: { bullet: string }[];
}

export function AIOutputDisplay({ output }: { output: any }) {
    const data = output.output_json;
    const kind = output.kind;

    if (kind === 'parse_jd') {
        const jd = data as ParsedJD;
        return (
            <div className="space-y-4 text-sm">
                <h4 className="font-bold text-lg">{jd.title}</h4>
                <div>
                    <h5 className="font-semibold text-green-700">Must Have</h5>
                    <ul className="list-disc pl-5">
                        {jd.must_have_skills.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                </div>
                <div>
                    <h5 className="font-semibold text-blue-700">Nice to Have</h5>
                    <ul className="list-disc pl-5">
                        {jd.nice_to_have_skills.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                </div>
            </div>
        );
    }

    if (kind === 'match') {
        const match = data as MatchResult;
        return (
            <div className="space-y-4 text-sm">
                <div className="flex items-center gap-2">
                    <div className="text-xl font-bold">{match.match_score}% Match</div>
                    <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600" style={{ width: `${match.match_score}%` }}></div>
                    </div>
                </div>
                <div className="bg-blue-50 p-3 rounded text-blue-900 italic">
                    "{match.tailored_angle}"
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <h5 className="font-semibold text-green-700">Strong Matches</h5>
                        <ul className="list-disc pl-5">
                            {match.strong_matches.map((s, i) => <li key={i}>{s.item}</li>)}
                        </ul>
                    </div>
                    <div>
                        <h5 className="font-semibold text-red-700">Missing / Gaps</h5>
                        <ul className="list-disc pl-5">
                            {match.missing_skills.map((s, i) => <li key={i}>{s.item}</li>)}
                        </ul>
                    </div>
                </div>
            </div>
        );
    }

    if (kind === 'tailor_cv') {
        const cv = data as TailoredCV;
        return (
            <div className="space-y-4 text-sm">
                <h5 className="font-semibold">Suggested Bullets</h5>
                <ul className="list-disc pl-5 space-y-2">
                    {cv.bullet_suggestions.map((s, i) => (
                        <li key={i} className="text-gray-800 bg-gray-50 p-2 rounded border border-gray-100">
                            {s.bullet}
                        </li>
                    ))}
                </ul>
            </div>
        );
    }

    return <pre className="text-xs">{JSON.stringify(data, null, 2)}</pre>;
}
