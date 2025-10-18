'use client'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import DiffViewer from '@/components/DiffViewer'
export default function TicketDetail(){
  const { key } = useParams<{key:string}>()
  const [mu,setMu]=useState(0.4); const [diff,setDiff]=useState('')
  const base=process.env.NEXT_PUBLIC_API_BASE||''
  const load=async(v=mu)=>{ const r=await fetch(`${base}/api/demo/diff?key=${key}&mu=${v}`); const text=await r.text(); setDiff(text) }
  useEffect(()=>{load()},[])
  return (<main className="space-y-4"><h1 className="text-2xl font-semibold">Ticket {key}</h1><div className="bg-white shadow ring-1 ring-black/10 rounded-2xl p-4"><div className="text-sm mb-2">Mimicness (µ): {mu.toFixed(2)}</div><input type="range" min={0} max={1} step={0.05} value={mu} onChange={e=>setMu(parseFloat(e.target.value))}/><button onClick={()=>load()} className="ml-3 px-3 py-1 rounded bg-blue-600 text-white text-sm">Generate Patch</button></div>{diff?<DiffViewer diff={diff}/>:<div className="rounded-2xl p-4 bg-black text-green-200">No diff generated yet.</div>}</main>)
}
