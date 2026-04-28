import axios from 'axios'

const client = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/v1',
    headers: {
        'Content-Type': 'application/json'
    },
})

// Orgs
export const ingestCSV = (orgSlug, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post(`/ingest/${orgSlug}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data'},
    })
}

// Users
export const getUsers = (orgSlug) =>
    client.get(`/users/${orgSlug}`)


export const getUserRisk = (orgSlug, userId) =>
    client.get(`/users/${orgSlug}/${userId}/risk`)



// Scans
export const triggerScan = (orgSlug) =>
    client.post(`/scans/${orgSlug}/run`)

export const getScans = (orgSlug) =>
    client.get(`/scans/${orgSlug}`)

export default client