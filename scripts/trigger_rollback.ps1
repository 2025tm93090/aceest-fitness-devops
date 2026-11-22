# Automated Rollback Controller (PowerShell for Windows)
# Course: CSIZG514/SEZG514 DevOps Assignment 2
$Namespace = "aceest-fitness"
$Deployment = "aceest-app"

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "      ACEest Fitness - Automated Rollback Controller      " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Red

Write-Host "[*] Current Deployment Revision History:" -ForegroundColor Gray
kubectl rollout history deployment/$Deployment -n $Namespace

Write-Host "`n[!] Triggering Rollout Undo to revert to the last stable revision..." -ForegroundColor Yellow
kubectl rollout undo deployment/$Deployment -n $Namespace

Write-Host "[*] Monitoring rollback progress..." -ForegroundColor Gray
kubectl rollout status deployment/$Deployment -n $Namespace --timeout=120s

Write-Host "`n[SUCCESS] Rollback verified! Current running revision pods:" -ForegroundColor Green
kubectl get pods -n $Namespace -l app=aceest-fitness
