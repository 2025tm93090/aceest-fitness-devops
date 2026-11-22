#!/bin/bash
# Automated Kubernetes Rollback Script for ACEest Fitness
# Course: CSIZG514/SEZG514 DevOps Assignment 2
set -e

NAMESPACE="aceest-fitness"
DEPLOYMENT_NAME="aceest-app"

echo "=========================================================="
echo "      ACEest Fitness - Automated Rollback Controller      "
echo "=========================================================="

echo "[*] Current Deployment Revision History:"
kubectl rollout history deployment/$DEPLOYMENT_NAME -n $NAMESPACE

echo ""
echo "[!] Triggering Rollout Undo to revert to the last stable revision..."
kubectl rollout undo deployment/$DEPLOYMENT_NAME -n $NAMESPACE

echo "[*] Monitoring rollback progress..."
kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE --timeout=120s

echo ""
echo "[SUCCESS] Rollback verified! Current running revision pods:"
kubectl get pods -n $NAMESPACE -l app=aceest-fitness
