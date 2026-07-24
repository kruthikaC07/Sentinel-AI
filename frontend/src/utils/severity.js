export const severityClasses = {
  Critical: "bg-red-100 text-red-700 ring-red-200",
  High: "bg-orange-100 text-orange-700 ring-orange-200",
  Medium: "bg-yellow-100 text-yellow-800 ring-yellow-200",
  Low: "bg-green-100 text-green-700 ring-green-200"
};

export function severityBadge(severity) {
  return severityClasses[severity] || severityClasses.Medium;
}
