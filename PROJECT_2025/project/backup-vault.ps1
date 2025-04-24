$env:VAULT_ADDR = "http://127.0.0.1:8200"
$backupFile = "vault_backup.json"
$allSecrets = @{}

$keys = vault kv list -format=json secret/ | jq -r '.[]'

foreach ($key in $keys) {
    $secretJson = vault kv get -format=json secret/$key | ConvertFrom-Json
    $secretData = $secretJson.data.data
    $allSecrets[$key] = $secretData
}

$allSecrets | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 $backupFile
Write-Output "✅ All secrets backed up to $backupFile"
