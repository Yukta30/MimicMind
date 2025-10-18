import Link from 'next/link'
const tickets=[{key:'DEMO-1',summary:'Fix pagination boundary in Pager'},{key:'DEMO-2',summary:'Add logging to Exporter'}]
export default function Tickets(){
  return (<main className="space-y-4"><h1 className="text-2xl font-semibold">Tickets</h1><ul className="space-y-2">{tickets.map(t=>(<li key={t.key} className="rounded-xl bg-white shadow ring-1 ring-black/10 p-4 flex justify-between"><div><div className="font-medium">{t.key}</div><div className="text-sm text-gray-600">{t.summary}</div></div><Link className="text-blue-600 underline" href={`/tickets/${t.key}`}>Open</Link></li>))}</ul></main>)
}
