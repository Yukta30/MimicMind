import Link from 'next/link'
function Card({title,value,subtitle}:{title:string;value:string;subtitle:string}){
  return (<div className="rounded-2xl shadow p-4 bg-white ring-1 ring-black/10"><div className="text-sm text-gray-500">{title}</div><div className="text-3xl font-bold">{value}</div><div className="text-xs text-gray-500">{subtitle}</div></div>)
}
export default function Dashboard(){
  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div><h1 className="text-2xl font-semibold">MimicMind Demo</h1><p className="text-gray-500">AI that codes like you — bugs and all.</p></div>
        <div className="flex gap-4 text-sm"><Link className="text-blue-600 underline" href="/tickets">View Tickets</Link><Link className="text-blue-600 underline" href="/workbench">Open Workbench</Link></div>
      </header>
      <div className="grid md:grid-cols-3 gap-4"><Card title="Style Match" value="0.83" subtitle="Last PR"/><Card title="Tests Passing" value="98%" subtitle="Demo suite"/><Card title="Mimicness" value="μ = 0.40" subtitle="Best‑practice tilt"/></div>
    </div>)
}
