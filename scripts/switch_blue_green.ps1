# Blue-Green Traffic Switch Script (PowerShell for Windows)
# Course: CSIZG514/SEZG514 DevOps Assignment 2
$Namespace = "aceest-fitness"
$ServiceName = "aceest-bluegreen-service"

Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "    ACEest Fitness - Blue/Green Traffic Switch Engine    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Yellow

# 1. Detect current slot
$CurrentSlot = (kubectl get svc $ServiceName -n $Namespace -o jsonpath='{.spec.selector.app-version}' 2>$null)
if (-not $CurrentSlot) { $CurrentSlot = "blue" }
Write-Host "[*] Current Active Production Slot: $($CurrentSlot.ToUpper())" -ForegroundColor Green

if ($CurrentSlot -eq "blue") {
    $TargetSlot = "green"
} else {
    $TargetSlot = "blue"
}

Write-Host "[*] Target Deployment Slot for Switch: $($TargetSlot.ToUpper())" -ForegroundColor Cyan

# 2. Check readiness of target deployment
Write-Host "[*] Checking readiness of $($TargetSlot.ToUpper()) pods..." -ForegroundColor Gray
kubectl rollout status deployment/aceest-$TargetSlot -n $Namespace --timeout=60s

# 3. Patch service selector
Write-Host "[*] Switching traffic atomically to $($TargetSlot.ToUpper())..." -ForegroundColor Yellow
$patchJson = '{"spec":{"selector":{"app":"aceest-bluegreen","app-version":"' + $TargetSlot + '"}}}'
kubectl patch service $ServiceName -n $Namespace -p $patchJson

# 4. Verify
Start-Sleep -Seconds 2
$ActiveSlotNow = (kubectl get svc $ServiceName -n $Namespace -o jsonpath='{.spec.selector.app-version}')

if ($ActiveSlotNow -eq $TargetSlot) {
    Write-Host "[SUCCESS] Cutover complete! Live traffic is now served by: $($TargetSlot.ToUpper())" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Switch failed! Reverting back to $($CurrentSlot.ToUpper())..." -ForegroundColor Red
    $rollbackPatch = '{"spec":{"selector":{"app":"aceest-bluegreen","app-version":"' + $CurrentSlot + '"}}}'
    kubectl patch service $ServiceName -n $Namespace -p $rollbackPatch
    exit 1
}
