import { useState, useEffect } from 'react'
import { getUsers, getScans, triggerScan } from '../api/client'

const riskColor = (label) => {
  if (label === 'critical') return { bg: '#FCEBEB', text: '#A32D2D' }
  if (label === 'high') return { bg: '#FAEEDA', text: '#854F0B' }
  if (label === 'medium') return { bg: '#E6F1FB', text: '#185FA5' }
  return { bg: '#EAF3DE', text: '#3B6D11' }
}

export default function Dashboard({ orgSlug }) {
    const [users, setUsers] = useState([])
    const [scans, setScans] = useState([])
    const [loading, setLoading] = useState(true)


    useEffect(() => {
    Promise.all([getUsers(orgSlug), getScans(orgSlug)])
      .then(([usersRes, scansRes]) => {
        setUsers(usersRes.data)
        setScans(scansRes.data)
      })
        .finally(() => setLoading(false))
    }, [orgSlug])

    if (loading) return <p style={{ color: 'var(--color-text-secondary) '}}>Loading...</p>

    const latestScan = scans[0]
    const totalViolations = latestScan?.violations_found ?? 0
    const lastScanTime = latestScan
        ? new Date(latestScan.started_at).toLocaleString()
        : 'Never'

    return (
        <div>
            {/* Metric cards */}
            <div style= {{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
                <div style= {{ background: 'var(--color-background-secondary)', borderRadius: '8px', padding: '14px 16px' }}>
                    <p style= {{fontSize: '12px', color: 'var(--color-text-secondary)', margin: '0 0 4px' }}>Total users</p>
                    <p style={{ fontSize: '24px', fontWeight: '500', margin: 0 }}>{users.length}</p>
                </div>
                <div style = {{background: 'var(--color-background-secondary)', borderRadius: '8px', padding: '14px 16px '}}>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '0 0 4px' }}>SoD violations</p>
                    <p style={{ fontSize: '24px', fontWeight: '500', margin: 0, color: '#A32D2D' }}>{totalViolations}</p>
                </div>
                <div style={{ background: 'var(--color-background-secondary)', borderRadius: '8px', padding: '14px 16px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '0 0 4px' }}>Total scans</p>
                    <p style={{ fontSize: '24px', fontWeight: '500', margin: 0 }}>{scans.length}</p>
                </div>
                <div style={{ background: 'var(--color-background-secondary)', borderRadius: '8px', padding: '14px 16px' }}>
                    <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '0 0 4px' }}>Last scan</p>
                    <p style={{ fontSize: '13px', fontWeight: '500', margin: 0 }}>{lastScanTime}</p>
                </div>
            </div>

            {/* Users table */}

            <div style={{ background: 'var(--color-background-primary)', border: '0.5px solid var(--color-border-tertiary)', borderRadius: '12px', overflow: 'hidden' }}>
                <div style={{ padding: '14px 16px', borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
                    <p style={{ fontSize: '13px', fontWeight: '500', margin: 0 }}>Users</p>
                </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
                <tr style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
                <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Name</th>
                <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Department</th>
                <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Job title</th>
                <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Type</th>
                </tr>
            </thead>
            <tbody>
                {users.map((user) => (
                <tr key={user.id} style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
                    <td style={{ padding: '10px 16px' }}>{user.full_name}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.department}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.job_title}</td>
                    <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.employee_type}</td>
                </tr>
                ))}
            </tbody>
            </table>
        </div>
    </div>
    )
}