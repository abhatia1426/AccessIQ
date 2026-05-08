import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Scans from './pages/Scans'

const ORG_SLUG = 'acme-corp'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: '#0f0f0f' }}>
        <Navbar orgSlug={ORG_SLUG} />
        <main style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard orgSlug={ORG_SLUG} />} />
            <Route path="/users" element={<Users orgSlug={ORG_SLUG} />} />
            <Route path="/scans" element={<Scans orgSlug={ORG_SLUG} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}