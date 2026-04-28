import { useState, useEffect } from 'react'
import { getScans } from '../api/client'

export default function Scans({ orgSlug }) {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getScans(orgSlug)
      .then((res) => setScans(res.data))
      .finally(() => setLoading(false))
  }, [orgSlug])

  if (loading) return <p style={{ color: 'var(--color-text-secondary)' }}>Loading...</p>

  return (
    <div>
      <div style={{ background: 'var(--color-background-primary)', border: '0.5px solid var(--color-border-tertiary)', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ padding: '14px 16px', borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
          <p style={{ fontSize: '13px', fontWeight: '500', margin: 0 }}>Scan history</p>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Scan ID</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Status</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Users scanned</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Violations</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Started</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.id} style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                  {scan.id.slice(0, 8)}...
                </td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{
                    fontSize: '11px', padding: '3px 8px', borderRadius: '6px',
                    background: scan.status === 'completed' ? '#EAF3DE' : '#FAEEDA',
                    color: scan.status === 'completed' ? '#3B6D11' : '#854F0B',
                  }}>
                    {scan.status}
                  </span>
                </td>
                <td style={{ padding: '10px 16px' }}>{scan.users_scanned}</td>
                <td style={{ padding: '10px 16px', color: scan.violtions_found > 0 ? '#A32D2D' : 'var(--color-text-primary)' }}>
                  {scan.violtions_found}
                </td>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>
                  {new Date(scan.started_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}