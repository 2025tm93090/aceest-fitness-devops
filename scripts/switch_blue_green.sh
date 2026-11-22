#!/bin/bash
# Blue-Green Zero-Downtime Traffic Switching Script
# Course: CSIZG514/SEZG514 DevOps Assignment 2
set -e

NAMESPACE="aceest-fitness"
SERVICE_NAME="aceest-bluegreen-service"

echo "=========================================================="
echo "    ACEest Fitness - Blue/Green Traffic Switch Engine    "
echo "=========================================================="

# 1. Detect current active slot
CURRENT_SLOT=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.selector.app-version}' 2>/dev/null || echo "blue")
echo "[*] Current Active Production Slot: ${CURRENT_SLOT^^}"

if [ "$CURRENT_SLOT" == "blue" ]; then
    TARGET_SLOT="green"
else
    TARGET_SLOT="blue"
fi

echo "[*] Target Deployment Slot for Switch: ${TARGET_SLOT^^}"

# 2. Verify target pods are in Ready status
echo "[*] Verifying readiness of ${TARGET_SLOT^^} pods..."
kubectl rollout status deployment/aceest-${TARGET_SLOT} -n $NAMESPACE --timeout=60s

# 3. Perform atomic service selector switch
echo "[*] Switching live traffic from ${CURRENT_SLOT^^} -> ${TARGET_SLOT^^}..."
kubectl patch service $SERVICE_NAME -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"app\":\"aceest-bluegreen\",\"app-version\":\"${TARGET_SLOT}\"}}}"

# 4. Smoke test validation
echo "[*] Running post-switch health probe..."
sleep 2
ACTIVE_SLOT_NOW=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.selector.app-version}')

if [ "$ACTIVE_SLOT_NOW" == "$TARGET_SLOT" ]; then
    echo "[SUCCESS] Zero-downtime cutover complete! Live traffic is now served by: ${TARGET_SLOT^^}"
else
    echo "[ERROR] Failed to switch service selector! Reverting to ${CURRENT_SLOT^^}..."
    kubectl patch service $SERVICE_NAME -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"app\":\"aceest-bluegreen\",\"app-version\":\"${CURRENT_SLOT}\"}}}"
    exit 1
fi
