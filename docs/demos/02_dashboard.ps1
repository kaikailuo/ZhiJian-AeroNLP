$ErrorActionPreference = "Stop"

$baseUrl = $env:AERONLP_API_BASE_URL
if (-not $baseUrl) { $baseUrl = "http://localhost:8000/api/v1" }

$login = curl -s -X POST "$baseUrl/auth/login" -H "Content-Type: application/json" -d '{"email":"admin@aeronlp.local","password":"admin123"}' | ConvertFrom-Json
$token = $login.access_token

Write-Host "Dashboard summary:"
$summary = curl -s -X GET "$baseUrl/dashboard/summary" -H "Authorization: Bearer $token"
$summary
