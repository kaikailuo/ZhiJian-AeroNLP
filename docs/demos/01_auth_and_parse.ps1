$ErrorActionPreference = "Stop"

$baseUrl = $env:AERONLP_API_BASE_URL
if (-not $baseUrl) { $baseUrl = "http://localhost:8000/api/v1" }

Write-Host "Register demo user..."
try {
  curl -s -X POST "$baseUrl/auth/register" -H "Content-Type: application/json" -d '{"email":"demo@aeronlp.local","password":"demo123"}' | Out-Null
} catch {}

Write-Host "Login demo user..."
$login = curl -s -X POST "$baseUrl/auth/login" -H "Content-Type: application/json" -d '{"email":"demo@aeronlp.local","password":"demo123"}' | ConvertFrom-Json
$token = $login.access_token

Write-Host "Parse NOTAM text..."
$parse = curl -s -X POST "$baseUrl/notam/parse" -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d '{"raw_text":"A) ZBAA E) RWY 18L/36R CLOSED DUE TO MAINTENANCE"}'
$parse
