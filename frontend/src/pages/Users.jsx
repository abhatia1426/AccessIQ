import { useState, useEffect } from 'react'
import { getUsers } from '../api/client'

export default function Users({ orgSlug }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getUsers(orgSlug)
      .then((res) => setUsers(res.data))
      .finally(() => setLoading(false))
  }, [orgSlug])

  if (loading) return <p style={{ color: 'var(--color-text-secondary)' }}>Loading...</p>

  return (
    <div>
      <div style={{ background: 'var(--color-background-primary)', border: '0.5px solid var(--color-border-tertiary)', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ padding: '14px 16px', borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
          <p style={{ fontSize: '13px', fontWeight: '500', margin: 0 }}>All users</p>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Name</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Email</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Department</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Job title</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Type</th>
              <th style={{ textAlign: 'left', padding: '10px 16px', fontWeight: '500', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} style={{ borderBottom: '0.5px solid var(--color-border-tertiary)' }}>
                <td style={{ padding: '10px 16px', fontWeight: '500' }}>{user.full_name}</td>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.email}</td>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.department}</td>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.job_title}</td>
                <td style={{ padding: '10px 16px', color: 'var(--color-text-secondary)' }}>{user.employee_type}</td>
                <td style={{ padding: '10px 16px' }}>
                  <span style={{
                    fontSize: '11px', padding: '3px 8px', borderRadius: '6px',
                    background: user.is_active ? '#EAF3DE' : '#F1EFE8',
                    color: user.is_active ? '#3B6D11' : '#5F5E5A',
                  }}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}