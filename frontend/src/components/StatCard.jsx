export default function StatCard({ label, value, tone = "navy" }) {
  const tones = {
    navy: "border-navy-100 bg-navy-50 text-navy-900",
    red: "border-red-100 bg-red-50 text-red-700",
    green: "border-green-100 bg-green-50 text-green-700",
    amber: "border-amber-100 bg-amber-50 text-amber-700"
  };

  return (
    <div className={`rounded-lg border p-4 ${tones[tone]}`}>
      <p className="text-sm font-semibold opacity-75">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}
