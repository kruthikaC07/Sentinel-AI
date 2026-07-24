import { CheckCircle2, Loader2 } from "lucide-react";

export const reportSteps = [
  "Uploading Report...",
  "Analyzing Image...",
  "Understanding Incident...",
  "Determining Severity...",
  "Selecting Best Responder...",
  "Creating Incident...",
  "Notifying Registered Responders...",
  "Completed"
];

export default function LoadingSteps({ activeStep = 0, completed = false }) {
  const progress = completed ? 100 : Math.min(96, ((activeStep + 1) / reportSteps.length) * 100);
  return (
    <div className="rounded-lg border border-navy-100 bg-white p-5 shadow-command">
      <div className="mb-4 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-navy-800 transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>
      <div className="space-y-3">
        {reportSteps.map((step, index) => (
          <div key={step} className="flex items-center justify-between gap-3 text-sm font-semibold">
            <span className={index <= activeStep || completed ? "text-navy-900" : "text-slate-400"}>{step}</span>
            {index <= activeStep || completed ? (
              <CheckCircle2 size={18} className="text-green-600" />
            ) : index === activeStep + 1 ? (
              <Loader2 size={18} className="animate-spin text-navy-800" />
            ) : (
              <span className="h-4 w-4 rounded-full border border-slate-300" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
