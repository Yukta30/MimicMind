'use client'
import React from 'react'
function cls(...xs:(string|false)[]){return xs.filter(Boolean).join(' ')}
export default function DiffViewer({diff}:{diff:string}){
  const lines = diff.split('\n')
  return (
    <div className="rounded-2xl overflow-hidden bg-[#0b0f14] shadow ring-1 ring-black/10">
      <div className="px-4 py-2 text-xs text-gray-300 bg-black/40 border-b border-white/10">Proposed Diff</div>
      <pre className="text-sm leading-5 m-0">
        {lines.map((line,i)=>{
          const type = line.startsWith('+')?'add':line.startsWith('-')?'del':line.startsWith('@@')?'hunk':(line.startsWith('---')||line.startsWith('+++'))?'file':'ctx'
          return (
            <div key={i} className={cls('whitespace-pre flex font-mono',type==='add'&&'bg-green-900/20',type==='del'&&'bg-red-900/20',type==='hunk'&&'bg-blue-900/20 text-blue-200',type==='file'&&'bg-black/30 text-gray-300')}>
              <span className="select-none w-12 shrink-0 text-right pr-3 text-xs text-gray-500 border-r border-white/10">{i+1}</span>
              <span className="px-3 py-0.5 text-gray-200">{line}</span>
            </div>
          )
        })}
      </pre>
    </div>
  )
}
