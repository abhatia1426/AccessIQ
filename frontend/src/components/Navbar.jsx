import { Link, useLocation } from 'react-router-dom'
import { triggerScan } from '../api/client'
import { useState } from 'react'

export default function Navbar({ orgSlug }) {
    const location = useLocation()
    const [scanning, setScanning] = useState(false)

    const handleScan = async() => {
        setScanning(true)
        try {
            await triggerScan(orgSlug)
            alert('Scan completed successfully!')
        } catch (err) {
            alert('Scan failed: ' + err.message)
        } finally {
            setScanning(false)
        }
    }

    const navLink = (path, label) => (
        <Link
            to={path}
            style={{
                fontSize: '13px',
                padding: '6px 12px',
                borderRadius: '8px',
                textDecoration: 'none',
                background: location.pathname === path ? 'var(--color--background-secondary)' : 'transparent',
                color: location.pathname === path ? 'var(--color-text-primary)' : 'var(--color-text-secondary',
            }}
        >
            {label}
        </Link>
    )

    return (
        <nav style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '12px 20px',
            borderBottom: '0.5px solid var(--color-border-tertiary)',
            background: 'var(--color-background-primary)'
        }}>
            <div style = {{ display: 'flex', alignItems: 'center', gap: '24px' }}>
                <span style={{ fontSize: '15px', fontWeight: '500' }}>AccessIQ</span>
                <div style={{display: 'flex', gap: '4px '}}>
                    {navLink('/dashboard', 'Dashboard')}
                    {navLink('/users', 'Users')}
                    {navLink('/scans', 'Scans')}
                </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                    {orgSlug}
                </span>
                <button
                    onClick={handleScan}
                    disabled={scanning}
                    style={{
                        fontSize: '12px',
                        padding: '6px 14px',
                        borderRadius: '8px',
                        background: '#533A87',
                        color: '#EEEDFE',
                        cursor: scanning ? 'not-allowed' : 'pointer',
                        opacity: scanning ? 0.7 : 1
                    }}
                >
                    {scanning ? 'Scanning...' : 'Run Scan'}
                </button>
            </div>
        </nav>
    )
}