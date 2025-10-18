'use client'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function TicketDetail(){
  const { key } = useParams<{key:string}>()
  const [mu, setMu] = useState(0.4)
  const [diff, setDiff] = useState('')
  const base = process.env.NEXT_PUBLIC_API_BASE || ''

  const load = async (value = mu) => {
    const r = await fetch(`${base}/api/demo/diff?key=${key}&mu=${value}`)
    const text = await r.text() // keep as .text() since API now returns PlainTextResponse
    setDiff(text)
  }

  // Debounce: auto-refresh 300ms after slider stops moving
  useEffect(() => {
    const t = setTimeout(() => load(mu), 300)
    return () => clearTimeout(t)
  }, [mu])

  return (
    <main className="p-6 space-y-4 max-w-5xl mx-auto">
      <h1 className="text-2xl font-semibold">Ticket {key}</h1>
      <div className="bg-white shadow rounded-2xl p-4">
        <div className="text-sm mb-2">Mimicness (µ): {mu.toFixed(2)}</div>
        <input type="range" min={0} max={1} step={0.05}
               value={mu}
               onChange={e => setMu(parseFloat(e.target.value))} />
        <button onClick={() => load()} className="ml-3 px-3 py-1 rounded bg-black text-white text-sm">
          Generate Patch
        </button>
      </div>
      <pre className="rounded-2xl p-4 overflow-auto bg-black text-green-200 whitespace-pre text-sm">
        {diff || 'No diff generated yet.'}
      </pre>
    </main>
  )
}
