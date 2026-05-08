import { useState, useEffect } from 'react'
import { getUsers, getScans } from '../api/client'

const riskColors = {
  critical: { bg: '#2d1515', text: '#f87171', border: '#5c2020' },
  high:     { bg: '#2d1f0f', text: '#fb923c', border: '#5c3a0f' },
  medium:   { bg: '#0f1f2d', text: '#60a5fa', border: '#0f3a5c' },
  low:      { bg: '#0f2d1a', text: '#4ade80', border: '#0f5c2a' },
}

const MetricCard = ({ label, value, valueColor }) => (
  <div style={{
    background: '#161616',
    border: '1px solid #222',
    borderRadius: '10px',
    padding: '20px 24px',
  }}>
    <p style={{ fontSize: '12px', color: '#555', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</p>
    <p style={{ fontSize: '28px', fontWeight: '600', color: valueColor || '#fff', letterSpacing: '-0.5px' }}>{value}</p>
  </div>
)

const RiskBadge = ({ label }) => {
  if (!label) return <span style={{ color: '#444' }}>—</span>
  const c = riskColors[label] || riskColors.low
  return (
    <span style={{
      fontSize: '11px',
      padding: '3px 8px',
      borderRadius: '5px',
      background: c.bg,
      color: c.text,
      border: `1px solid ${c.border}`,
      fontWeight: '500',
      textTransform: 'uppercase',
      letterSpacing: '0.4px',
    }}>
      {label}
    </span>
  )
}

export default function Dashboard({ orgSlug }) {
  const [users, setUsers] = useState([])
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getUsers(orgSlug), getScans(orgSlug)])
      .then(([u, s]) => { setUsers(u.data); setScans(s.data) })
      .finally(() => setLoading(false))
  }, [orgSlug])

  if (loading) return <p style={{ color: '#555', padding: '40px 0' }}>Loading...</p>

  const latestScan = scans[0]
  const totalViolations = latestScan?.violations_found ?? 0
  const lastScanTime = latestScan ? new Date(latestScan.started_at).toLocaleString() : 'Never'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        <MetricCard label="Total users" value={users.length} />
        <MetricCard label="SoD violations" value={totalViolations} valueColor={totalViolations > 0 ? '#f87171' : '#fff'} />
        <MetricCard label="Total scans" value={scans.length} />
        <MetricCard label="Last scan" value={lastScanTime} />
      </div>

      <div style={{ background: '#161616', border: '1px solid #222', borderRadius: '10px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #222', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <p style={{ fontSize: '13px', fontWeight: '500', color: '#fff' }}>Users</p>
          <p style={{ fontSize: '12px', color: '#555' }}>{users.length} total</p>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e1e1e' }}>
              {['Name', 'Department', 'Job title', 'Type', 'Violations', 'Risk score', 'Risk label'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 24px', fontWeight: '500', color: '#555', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.4px' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map((user, i) => (
              <tr key={user.id} style={{ borderBottom: i < users.length - 1 ? '1px solid #1a1a1a' : 'none', transition: 'background 0.1s' }}
                onMouseEnter={e => e.currentTarget.style.background = '#1a1a1a'}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <td style={{ padding: '12px 24px', fontWeight: '500', color: '#e8e8e8' }}>{user.full_name}</td>
                <td style={{ padding: '12px 24px', color: '#888' }}>{user.department}</td>
                <td style={{ padding: '12px 24px', color: '#888' }}>{user.job_title}</td>
                <td style={{ padding: '12px 24px', color: '#666' }}>{user.employee_type}</td>
                <td style={{ padding: '12px 24px', color: user.sod_violation_count > 0 ? '#f87171' : '#888' }}>{user.sod_violation_count ?? 0}</td>
                <td style={{ padding: '12px 24px', color: '#e8e8e8' }}>{user.overall_score?.toFixed(0) ?? '—'}</td>
                <td style={{ padding: '12px 24px' }}><RiskBadge label={user.risk_label} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}