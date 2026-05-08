import { Link, useLocation } from 'react-router-dom'
import { triggerScan } from '../api/client'
import { useState } from 'react'

export default function Navbar({ orgSlug }) {
  const location = useLocation()
  const [scanning, setScanning] = useState(false)

  const handleScan = async () => {
    setScanning(true)
    try {
      await triggerScan(orgSlug)
      window.location.reload()
    } catch (err) {
      alert('Scan failed: ' + err.message)
    } finally {
      setScanning(false)
    }
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      height: '52px',
      background: '#161616',
      borderBottom: '1px solid #222',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '32px' }}>
        <span style={{ fontSize: '14px', fontWeight: '600', color: '#fff', letterSpacing: '-0.3px' }}>
          AccessIQ
        </span>
        <div style={{ display: 'flex', gap: '2px' }}>
          {['/dashboard', '/users', '/scans'].map((path) => (
            <Link key={path} to={path} style={{
              fontSize: '13px',
              padding: '5px 12px',
              borderRadius: '6px',
              color: isActive(path) ? '#fff' : '#888',
              background: isActive(path) ? '#222' : 'transparent',
              transition: 'all 0.15s',
            }}>
              {path.replace('/', '').charAt(0).toUpperCase() + path.slice(2)}
            </Link>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontSize: '12px', color: '#555' }}>{orgSlug}</span>
        <button onClick={handleScan} disabled={scanning} style={{
          fontSize: '12px',
          padding: '6px 14px',
          borderRadius: '6px',
          background: scanning ? '#333' : '#5b3fd4',
          color: scanning ? '#666' : '#fff',
          border: 'none',
          cursor: scanning ? 'not-allowed' : 'pointer',
          fontWeight: '500',
        }}>
          {scanning ? 'Scanning...' : 'Run scan'}
        </button>
      </div>
    </nav>
  )
}