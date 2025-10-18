'use client'
import { useEffect, useMemo, useState } from 'react'
import DiffViewer from '@/components/DiffViewer'
type Files = Record<string,string>
export default function Workbench(){
  const API=process.env.NEXT_PUBLIC_API_BASE||''
  const [files,setFiles]=useState<Files>({}); const [active,setActive]=useState('')
  const [mu,setMu]=useState(0.6); const [title,setTitle]=useState('Add robust paging to Pager')
  const [desc,setDesc]=useState('Users miss items at page boundaries. Ensure step uses size; add guard.')
  const [diff,setDiff]=useState('')
  useEffect(()=>{ fetch(`${API}/api/repo/demo`).then(r=>r.json()).then((d:Files)=>{setFiles(d); const f=Object.keys(d)[0]; if(f) setActive(f)}) },[API])
  const fileList=useMemo(()=>Object.keys(files).sort(),[files])
  const propose=async()=>{ const payload={ticket:{key:'WB-1',title,description:desc},files,mu}; const r=await fetch(`${API}/api/patch`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const text=await r.text(); setDiff(text) }
  return (<div className="space-y-6"><h1 className="text-2xl font-semibold">Workbench (Jira‑style)</h1><div className="grid lg:grid-cols-2 gap-6"><section className="bg-white rounded-2xl shadow ring-1 ring-black/10 overflow-hidden"><div className="border-b px-4 py-2 text-sm text-gray-600">Repository</div><div className="grid grid-cols-3"><aside className="border-r max-h-[60vh] overflow-auto">{fileList.map(p=>(<button key={p} onClick={()=>setActive(p)} className={`block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${active===p?'bg-gray-100 font-medium':''}`}>{p}</button>))}</aside><pre className="col-span-2 p-4 text-sm font-mono max-h-[60vh] overflow-auto bg-gray-50">{active?files[active]:'Select a file'}</pre></div></section><section className="bg-white rounded-2xl shadow ring-1 ring-black/10 p-4 space-y-3"><div className="text-sm text-gray-600">Ticket</div><input value={title} onChange={e=>setTitle(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="Ticket title"/><textarea value={desc} onChange={e=>setDesc(e.target.value)} className="w-full border rounded px-3 py-2 h-40 font-mono" placeholder="Describe the change needed…"/><div className="flex items-center gap-3"><div className="text-sm">Mimicness (µ): {mu.toFixed(2)}</div><input type="range" min={0} max={1} step={0.05} value={mu} onChange={e=>setMu(parseFloat(e.target.value))}/><button onClick={propose} className="ml-auto px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Propose Patch</button></div></section></div>{diff&&<DiffViewer diff={diff}/>}</div>)
}
