'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import DiffViewer from '@/components/DiffViewer'

type Files = Record<string, string>

const API = process.env.NEXT_PUBLIC_API_BASE || ''

// file extensions we’ll keep from uploads
const ACCEPT = [
  '.py','.ts','.tsx','.js','.jsx','.json','.md',
  '.go','.java','.rb','.rs','.cpp','.c','.cs','.php','.kt','.swift'
]

function keep(path: string) {
  const lower = path.toLowerCase()
  if (lower.includes('node_modules/')) return false
  if (lower.startsWith('.git/') || lower.includes('/.git/')) return false
  if (lower.includes('/build/') || lower.includes('/dist/')) return false
  return ACCEPT.some(ext => lower.endsWith(ext))
}

export default function Workbench() {
  // repo state
  const [files, setFiles] = useState<Files>({})
  const [active, setActive] = useState<string>('')

  // ticket + controls
  const [mu, setMu] = useState(0.6)
  const [title, setTitle] = useState('Add robust paging to Pager')
  const [desc, setDesc] = useState('Users miss items at page boundaries. Ensure step uses size; add guard.')

  // result + ui state
  const [diff, setDiff] = useState<string>('')
  const [err, setErr] = useState<string | null>(null)
  const [busy, setBusy] = useState<boolean>(false)

  // folder input (to set non-standard props safely)
  const folderRef = useRef<HTMLInputElement | null>(null)
  useEffect(() => {
    const el = folderRef.current as any
    if (!el) return
    el.webkitdirectory = true
    el.directory = true
    try {
      // safe fallback: only if setAttribute exists (avoids Chrome error you saw)
      if (typeof el.setAttribute === 'function') {
        el.setAttribute('webkitdirectory', 'true')
        el.setAttribute('directory', 'true')
      }
    } catch { /* ignore */ }
  }, [])

  // ---- load demo on first mount (nice first-run UX) ----
  const loadDemo = async () => {
    setErr(null)
    setBusy(true)
    try {
      const r = await fetch(`${API}/api/repo/demo`, { cache: 'no-store' })
      if (!r.ok) throw new Error(`Demo fetch failed: ${r.status}`)
      const json = await r.json() as Files
      setFiles(json)
      setActive(Object.keys(json)[0] || '')
      setDiff('')
    } catch (e: any) {
      console.error(e)
      setErr(e?.message || 'Failed to load demo')
      // tiny fallback so UI still works even if backend is down
      const fallback: Files = {
        'src/pager.py': [
          'class Pager:',
          '    def page(self, items, size):',
          '        pages = []',
          '        for i in range(0, len(items)):',
          '            if i % size == 0:',
          '                pages.append(items[i:i+size])',
          '        return pages',
        ].join('\n'),
        'README.md': '# Demo repo\n\nFallback demo when API is unreachable.',
      }
      setFiles(fallback)
      setActive('src/pager.py')
    } finally {
      setBusy(false)
    }
  }
  useEffect(() => { loadDemo() }, []) // initial load

  const fileList = useMemo(() => Object.keys(files).sort(), [files])

  // ---- Upload: local folder (client-side read) ----
  const onPickFolder = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files
    if (!list) return
    const map: Files = {}
    for (const f of Array.from(list)) {
      const rel = (f as any).webkitRelativePath || f.name
      if (!keep(rel)) continue
      const txt = await f.text()
      map[rel] = txt
    }
    setFiles(map)
    setActive(Object.keys(map)[0] || '')
    setDiff('')
    e.target.value = '' // reset input so selecting the same folder again works
  }

  // ---- Upload: .zip => backend returns {files, diff} ----
  const onPickZip = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setBusy(true)
    setErr(null)
    try {
      const form = new FormData()
      form.set('file', f)
      form.set('key', 'WB-1')
      form.set('title', title)
      form.set('description', desc)
      form.set('mu', String(mu))

      const r = await fetch(`${API}/api/patch-zip-json`, { method: 'POST', body: form })
      const contentType = r.headers.get('content-type') || ''
      if (!r.ok) throw new Error(`Zip upload failed: ${r.status}`)

      if (contentType.includes('application/json')) {
        const json = await r.json() as { files: Files, diff: string }
        // populate the left pane AND show the diff
        setFiles(json.files || {})
        setActive(Object.keys(json.files || {})[0] || '')
        setDiff(json.diff || '')
      } else {
        // legacy response (plain diff)
        const txt = await r.text()
        setDiff(txt)
      }
    } catch (e: any) {
      console.error(e)
      setErr(e?.message || 'Zip upload failed')
    } finally {
      setBusy(false)
      e.target.value = ''
    }
  }

  // ---- Propose patch from whatever is in memory (works for demo OR folder uploads) ----
  const propose = async () => {
    setBusy(true)
    setErr(null)
    try {
      const payload = { ticket: { key: 'WB-1', title, description: desc }, files, mu }
      const r = await fetch(`${API}/api/patch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const text = await r.text()
      setDiff(text)
    } catch (e: any) {
      console.error(e)
      setErr(e?.message || 'Failed to propose patch')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Workbench (Jira-style)</h1>

      {err && (
        <div className="rounded-md border border-amber-300 bg-amber-50 text-amber-900 px-3 py-2 text-sm">
          {err} — check <b>NEXT_PUBLIC_API_BASE</b> and your backend logs.
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Repository */}
        <section className="bg-white rounded-2xl shadow ring-1 ring-black/10 overflow-hidden">
          <div className="border-b px-4 py-2 text-sm text-gray-600 flex gap-2 items-center">
            <span className="mr-auto">Repository</span>

            <button
              onClick={loadDemo}
              disabled={busy}
              className="px-2 py-1 text-xs rounded bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
            >
              {busy ? 'Loading…' : 'Load demo'}
            </button>

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

            <label className="px-2 py-1 text-xs rounded bg-violet-50 hover:bg-violet-100 cursor-pointer">
              Upload .zip
              <input
                type="file"
                accept=".zip"
                className="hidden"
                onChange={onPickZip}
              />
            </label>
          </div>

          <div className="grid grid-cols-3">
            <aside className="border-r max-h-[60vh] overflow-auto">
              {fileList.length === 0 ? (
                <div className="p-3 text-sm text-gray-500">
                  No files loaded. Use <b>Upload folder</b> or <b>Upload .zip</b>.
                </div>
              ) : (
                fileList.map((p) => (
                  <button
                    key={p}
                    onClick={() => setActive(p)}
                    className={`block w-full text-left px-3 py-2 text-sm hover:bg-gray-50 ${
                      active === p ? 'bg-gray-100 font-medium' : ''
                    }`}
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
            onChange={(e) => setTitle(e.target.value)}
            className="w-full border rounded px-3 py-2"
            placeholder="Ticket title"
          />
          <textarea
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
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
              onChange={(e) => setMu(parseFloat(e.target.value))}
            />
            <button
              onClick={propose}
              disabled={busy}
              className="ml-auto px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {busy ? 'Proposing…' : 'Propose Patch'}
            </button>
          </div>
          <p className="text-xs text-gray-500">
            Tip: <b>Upload folder</b> keeps files client-side (we only send text when proposing).{' '}
            <b>Upload .zip</b> sends the archive to the backend, which returns both the{' '}
            file map and a proposed diff.
          </p>
        </section>
      </div>

      {diff && <DiffViewer diff={diff} />}
    </div>
  )
}
