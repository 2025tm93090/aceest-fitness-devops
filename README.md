# ACEest Fitness & Gym - DevOps CI/CD Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-black.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%2034%2F34%20Passing-brightgreen.svg)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-88%25-brightgreen.svg)](https://pytest-cov.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-5%20Deployments-326CE5.svg)](https://kubernetes.io/)
[![Jenkins](https://img.shields.io/badge/Jenkins-Declarative%20CI%2FCD-D24939.svg)](https://www.jenkins.io/)

> **Course:** Introduction to DevOps (Merged - CSIZG514 / SEZG514)  
> **Assignment:** Assignment - 2 (DevOps CI/CD Implementation)  
> **Company Profile:** ACEest Fitness & Gym (Coimbatore, Tamil Nadu)

---

## 1. Project Overview & Architecture

**ACEest Fitness & Gym** is a dynamic functional fitness startup undergoing digital transformation. This repository implements an industry-grade, test-driven, automated **Continuous Integration and Continuous Delivery (CI/CD)** pipeline covering:

- **Modular Web Application:** Foundational Flask application ported from the desktop Tkinter codebase, exposing REST APIs, health probes, and responsive Web UI with dark & gold branding.
- **Automated Testing:** Comprehensive Pytest test suite with 34 tests achieving **88% code coverage**.
- **Static Analysis & Quality Gate:** SonarQube integration with strict quality threshold enforcement.
- **Containerization:** Secure multi-stage Docker build running as an unprivileged non-root user (`appuser:appgroup`).
- **Progressive Delivery Topologies on Kubernetes:**
  1. **Rolling Update** (Zero-downtime standard with `maxSurge: 1`, `maxUnavailable: 0`)
  2. **Blue-Green Deployment** (Atomic cutover via Service selector switch)
  3. **Canary Release** (80% Stable / 20% Canary traffic split)
  4. **A/B Testing** (Layer 7 HTTP Header / Cookie routing)
  5. **Shadow Deployment** (Real-time traffic mirroring with zero user impact)
  6. **Automated Rollback** (Instant reversion using `kubectl rollout undo`)

---

## 2. Directory Structure

```text
aceest-devops/
├── ACEest_Fitness.py           # Application entrypoint (WSGI and CLI runner)
├── app/
│   ├── __init__.py             # Flask application factory and DB seed
│   ├── models.py               # SQLite data access layer (Clients, Workouts, Metrics, Progress)
│   ├── routes.py               # Web controllers & REST APIs (/health, /version, /api/clients)
│   ├── services.py             # Business logic (Calories, BMI classification, AI program generator, PDF/CSV)
│   ├── templates/              # Jinja2 HTML templates (Dark & Gold theme)
│   │   ├── base.html           # Master layout with health status badge
│   │   ├── index.html          # Workout programs & Tamil Nadu nutrition plans
│   │   ├── clients.html        # Member management & CSV/PDF export
│   │   ├── workouts.html       # Workout session and exercise tracking
│   │   ├── analytics.html      # Chart.js adherence trends & AI routine generator
│   │   └── deployments.html    # Interactive Kubernetes deployment strategies visualizer
│   └── static/                 # Static CSS and JS assets
├── tests/
│   ├── conftest.py             # Pytest fixtures and isolated test database
│   ├── test_models.py          # Database model and CRUD tests
│   ├── test_routes.py          # HTTP API endpoint tests
│   └── test_services.py        # Domain logic, BMI, and calorie formula tests
├── k8s/
│   ├── 00-namespace.yaml       # Namespace definition (aceest-fitness)
│   ├── 01-configmap.yaml       # Environment configuration
│   ├── 02-rolling-update.yaml  # Rolling Update Deployment & Service
│   ├── 03-blue-green.yaml      # Blue/Green Deployments & Switching Service
│   ├── 04-canary.yaml          # Canary 80/20 Deployment & Ingress
│   ├── 05-ab-testing.yaml      # A/B Testing Header-based Routing Ingress
│   ├── 06-shadow-deployment.yaml # Shadow Deployment with Traffic Mirroring
│   └── 07-hpa.yaml             # Horizontal Pod Autoscaler manifest
├── scripts/
│   ├── switch_blue_green.sh    # Linux/Mac Blue-Green traffic cutover script
│   ├── switch_blue_green.ps1   # Windows PowerShell Blue-Green switch script
│   ├── trigger_rollback.sh     # Automated rollback script
│   └── trigger_rollback.ps1    # Windows PowerShell rollback script
├── Dockerfile                  # Multi-stage production container build
├── .dockerignore               # Build context exclusions
├── docker-compose.yml          # Local orchestration for App + SonarQube + Jenkins
├── Jenkinsfile                 # Declarative CI/CD pipeline script
├── pytest.ini                  # Pytest test runner configuration
├── requirements.txt            # Python dependencies
├── sonar-project.properties    # SonarQube Scanner configuration
├── DEVOPS_REPORT.md            # Comprehensive 3-page technical submission report
└── README.md                   # Setup, execution, and verification guide
```

---

## 3. Quickstart & Local Execution

### 3.1 Python Local Environment Setup

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/aceest-fitness-devops.git
cd aceest-fitness-devops

# 2. Create virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python ACEest_Fitness.py
```
Open your browser at `http://localhost:5000` to interact with the dashboard.

### 3.2 Running Automated Pytest Suite & Coverage

```bash
# Run all 34 unit tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing --cov-report=xml:reports/coverage.xml --junitxml=reports/junit.xml
```

---

## 4. Containerization with Docker

### 4.1 Build Docker Images (Multi-Version Tagging)

```bash
# Build Release v1.0.0
docker build -t 2025tm93090/aceest-fitness:v1.0.0 .

# Build Release v2.0.0
docker build -t 2025tm93090/aceest-fitness:v2.0.0 .

# Build Release v3.0.0 and latest
docker build -t 2025tm93090/aceest-fitness:v3.0.0 -t 2025tm93090/aceest-fitness:latest .
```

### 4.2 Run Docker Container Locally

```bash
docker run -d --name aceest-app -p 5000:5000 2025tm93090/aceest-fitness:v3.0.0

# Verify health endpoint
curl http://localhost:5000/health
```

### 4.3 Push to Docker Hub

```bash
docker login
docker push 2025tm93090/aceest-fitness:v1.0.0
docker push 2025tm93090/aceest-fitness:v2.0.0
docker push 2025tm93090/aceest-fitness:v3.0.0
docker push 2025tm93090/aceest-fitness:latest
```

---

## 5. Kubernetes Deployment Strategies (Minikube / Cloud)

### 5.1 Initialize Namespace & Configuration

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
```

### 5.2 Strategy 1: Rolling Update (Zero Downtime)

```bash
# Apply rolling update deployment
kubectl apply -f k8s/02-rolling-update.yaml

# Check rollout status
kubectl rollout status deployment/aceest-app -n aceest-fitness

# Update to a new version smoothly:
kubectl set image deployment/aceest-app aceest-container=2025tm93090/aceest-fitness:v3.0.0 -n aceest-fitness
```

### 5.3 Strategy 2: Blue-Green Deployment

```bash
# Deploy both Blue and Green deployments + Router Service
kubectl apply -f k8s/03-blue-green.yaml

# Switch traffic between Blue and Green seamlessly:
# Linux/macOS:
./scripts/switch_blue_green.sh
# Windows PowerShell:
.\scripts\switch_blue_green.ps1
```

### 5.4 Strategy 3: Canary Release (80/20 Traffic Split)

```bash
# Deploy 4 Stable pods (80%) and 1 Canary pod (20%)
kubectl apply -f k8s/04-canary.yaml

# Observe traffic load distribution across pods
kubectl get pods -n aceest-fitness -l app=aceest-canary-app
```

### 5.5 Strategy 4: A/B Testing (Header Routing)

```bash
# Deploy Variant A (Control) and Variant B (Experiment)
kubectl apply -f k8s/05-ab-testing.yaml

# Test Control (Standard):
curl http://ab.aceest.local/

# Test Treatment (AI Generator via Header):
curl -H "X-Experiment: variant-b" http://ab.aceest.local/
```

### 5.6 Strategy 5: Shadow Deployment (Traffic Mirroring)

```bash
# Deploy Production and Shadow deployments with mirroring Ingress
kubectl apply -f k8s/06-shadow-deployment.yaml
```

### 5.7 Rollback Verification

```bash
# View rollout revision history
kubectl rollout history deployment/aceest-app -n aceest-fitness

# Trigger immediate rollback to last stable revision
kubectl rollout undo deployment/aceest-app -n aceest-fitness

# Alternatively run the automated script:
./scripts/trigger_rollback.sh
```

---

## 6. Jenkins CI/CD Pipeline Setup

1. In Jenkins, create a **New Item** $\rightarrow$ **Pipeline** $\rightarrow$ Name: `aceest-fitness-pipeline`.
2. Under **Build Triggers**, enable **Poll SCM** (`H/5 * * * *`) and **GitHub hook trigger for GITScm polling**.
3. Under **Pipeline Definition**, select **Pipeline script from SCM**:
   - SCM: **Git**
   - Repository URL: `https://github.com/<your-username>/aceest-fitness-devops.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
4. Add Credentials in Jenkins:
   - `docker-hub-credentials`: Docker Hub username and personal access token / password.
   - `SonarQubeServer`: Configured under Manage Jenkins $\rightarrow$ System $\rightarrow$ SonarQube servers.
5. Click **Build with Parameters** and choose deployment strategy (`RollingUpdate`, `BlueGreen`, `Canary`, etc.).

---

## 7. SonarQube Code Quality Gate

To run SonarQube analysis locally using Docker:
```bash
# Start SonarQube container
docker-compose up -d sonarqube

# Run sonar-scanner
sonar-scanner \
  -Dsonar.projectKey=aceest-fitness-app \
  -Dsonar.sources=app,ACEest_Fitness.py \
  -Dsonar.tests=tests \
  -Dsonar.python.coverage.reportPaths=reports/coverage.xml
```
Access the dashboard at `http://localhost:9000` (default login: `admin` / `admin`).

---

## 8. Git Branching & Tagging History

The repository follows a structured GitFlow branching strategy:
- `main`: Production releases (`v1.0.0`, `v2.0.0`, `v3.0.0`)
- `develop`: Ongoing integration
- Tags:
  - `v1.0.0`: Foundational web app & core fitness catalog
  - `v2.0.0`: Progress tracking & containerization
  - `v3.0.0`: Full DevOps CI/CD pipeline, Kubernetes deployment topologies & rollback mechanisms
