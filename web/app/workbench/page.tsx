'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import DiffViewer from '@/components/DiffViewer'

type Files = Record<string, string>

const ACCEPT = [
  '.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md',
  '.go', '.java', '.rb', '.rs', '.cpp', '.c', '.cs', '.php', '.kt', '.swift'
]

function keep(path: string) {
  const lower = path.toLowerCase()
  if (lower.includes('node_modules/')) return false
  if (lower.startsWith('.git/') || lower.includes('/.git/')) return false
  if (lower.includes('/build/') || lower.includes('/dist/')) return false
  return ACCEPT.some(ext => lower.endsWith(ext))
}

export default function Workbench() {
  const API = process.env.NEXT_PUBLIC_API_BASE || ''
  const [files, setFiles] = useState<Files>({})
  const [active, setActive] = useState('')
  const [mu, setMu] = useState(0.60)
  const [title, setTitle] = useState('Add robust paging to Pager')
  const [desc, setDesc] = useState('Users miss items at page boundaries. Ensure step uses size; add guard.')
  const [diff, setDiff] = useState('')

  // --- refs for folder input (to set non-standard attributes at runtime) ---
  const folderRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (folderRef.current) {
      // Add non-standard attributes so TS doesn't complain in JSX
      (folderRef.current as any).setAttribute('webkitdirectory', 'true')
      (folderRef.current as any).setAttribute('directory', 'true')
    }
  }, [])

  // Load demo repo initially (user can replace by upload)
  const loadDemo = async () => {
    const r = await fetch(`${API}/api/repo/demo`)
    const d: Files = await r.json()
    setFiles(d)
    setActive(Object.keys(d)[0] || '')
  }
  useEffect(() => { loadDemo() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const fileList = useMemo(() => Object.keys(files).sort(), [files])

  // --- Upload: folder (client-side read) ---
  const onPickFolder = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files
    if (!list) return
    const map: Files = {}
    for (const file of Array.from(list)) {
      // webkitRelativePath is supported by Chromium/WebKit
      const rel = (file as any).webkitRelativePath || file.name
      if (!keep(rel)) continue
      const txt = await file.text()
      map[rel] = txt
    }
    setFiles(map)
    setActive(Object.keys(map)[0] || '')
    setDiff('')
    e.target.value = '' // reset
  }

  // --- Upload: zip (send to backend) ---
  const onPickZip = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    const form = new FormData()
    form.set('file', f)
    form.set('key', 'WB-1')
    form.set('title', title)
    form.set('description', desc)
    form.set('mu', String(mu))
    const r = await fetch(`${API}/api/patch-zip`, { method: 'POST', body: form })
    const text = await r.text()
    setDiff(text)
    e.target.value = ''
  }

  // --- Propose patch with JSON files (folder upload path) ---
  const propose = async () => {
    const payload = { ticket: { key: 'WB-1', title, description: desc }, files, mu }
    const r = await fetch(`${API}/api/patch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const text = await r.text()
    setDiff(text)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Workbench (Jira-style)</h1>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Repository */}
        <section className="bg-white rounded-2xl shadow ring-1 ring-black/10 overflow-hidden">
          <div className="border-b px-4 py-2 text-sm text-gray-600 flex gap-2 items-center">
            <span className="mr-auto">Repository</span>

            {/* Load demo */}
            <button
              onClick={loadDemo}
              className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200"
            >
              Load demo
            </button>

            {/* Upload folder (TS-safe) */}
            <label className="px-2 py-1 text-xs rounded bg-blue-50 hover:bg-blue-100 cursor-pointer">
              Upload folder
              <input
                ref={folderRef}
                type="file"
                multiple
                className="hidden"
                onChange={onPickFolder}
              />
            </label>

            {/* Upload zip */}
            <label className="px-2 py-1 text-xs rounded bg-violet-50 hover:bg-violet-100 cursor-pointer">
              Upload .zip
              <input type="file" accept=".zip" className="hidden" onChange={onPickZip} />
            </label>
          </div>

          <div className="grid grid-cols-3">
            <aside className="border-r max-h-[60vh] overflow-auto">
              {fileList.length === 0 ? (
                <div className="p-3 text-sm text-gray-500">
                  No files loaded. Use <b>Upload folder</b> or <b>Upload .zip</b>.
                </div>
              ) : (
                fileList.map(p => (
                  <button
                    key={p}
                    onClick={() => setActive(p)}
                    className={`block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${active === p ? 'bg-gray-100 font-medium' : ''}`}
                  >
                    {p}
                  </button>
                ))
              )}
            </aside>
            <pre className="col-span-2 p-4 text-sm font-mono max-h-[60vh] overflow-auto bg-gray-50">
              {active ? files[active] : 'Select a file'}
            </pre>
          </div>
        </section>

        {/* Ticket */}
        <section className="bg-white rounded-2xl shadow ring-1 ring-black/10 p-4 space-y-3">
          <div className="text-sm text-gray-600">Ticket</div>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="Ticket title"
          />
          <textarea
            value={desc}
            onChange={e => setDesc(e.target.value)}
            className="w-full border rounded px-3 py-2 h-40 font-mono"
            placeholder="Describe the change needed…"
          />
          <div className="flex items-center gap-3">
            <div className="text-sm">Mimicness (µ): {mu.toFixed(2)}</div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={mu}
              onChange={e => setMu(parseFloat(e.target.value))}
            />
            <button
              onClick={propose}
              className="ml-auto px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
            >
              Propose Patch
            </button>
          </div>
          <p className="text-xs text-gray-500">
            Tip: <b>Upload folder</b> keeps files client-side and posts only text. <b>Upload .zip</b> sends the archive to the backend.
          </p>
        </section>
      </div>

      {diff && <DiffViewer diff={diff} />}
    </div>
  )
}
