import Link from 'next/link'

function Stat({title, value, subtitle}:{title:string;value:string;subtitle:string}){
  return (
    <div className="rounded-2xl shadow p-4 bg-white">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-xs text-gray-500">{subtitle}</div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <main className="p-6 space-y-6 max-w-5xl mx-auto">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">MimicMind Demo</h1>
        <Link href="/tickets" className="text-blue-600 underline">View Tickets</Link>
      </header>
      <div className="grid md:grid-cols-3 gap-4">
        <Stat title="Style Match" value="0.83" subtitle="Last PR" />
        <Stat title="Tests Passing" value="98%" subtitle="Demo suite" />
        <Stat title="Mimicness" value="µ = 0.40" subtitle="Best‑practice tilt" />
      </div>
    </main>
  )
}
