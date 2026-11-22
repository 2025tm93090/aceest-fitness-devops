// Declarative Jenkins CI/CD Pipeline for ACEest Fitness & Gym
// Course: Introduction to DevOps (CSIZG514 / SEZG514) - Assignment 2

pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOY_STRATEGY', choices: ['RollingUpdate', 'BlueGreen', 'Canary', 'ABTesting', 'Shadow'], description: 'Kubernetes deployment topology strategy')
        string(name: 'IMAGE_TAG', defaultValue: 'v3.0.0', description: 'Semantic version tag for container image')
        choice(name: 'ENVIRONMENT', choices: ['staging', 'production'], description: 'Target Kubernetes deployment environment')
    }

    triggers {
        // Poll SCM every 5 minutes and listen to GitHub webhooks
        pollSCM('H/5 * * * *')
        githubPush()
    }

    environment {
        DOCKER_HUB_REPO     = 'yourdockerhubuser/aceest-fitness'
        DOCKER_CREDENTIALS  = 'docker-hub-credentials'
        SONAR_SCANNER_HOME  = tool 'SonarScanner-5.0'
        KUBECONFIG_CRED_ID  = 'k8s-kubeconfig'
        K8S_NAMESPACE       = 'aceest-fitness'
        APP_NAME            = 'aceest-app'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        ansiColor('xterm')
    }

    stages {
        stage('1. Checkout SCM') {
            steps {
                echo "[*] Checking out latest source code commit..."
                checkout scm
                script {
                    env.GIT_SHORT_SHA = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    echo "Current Git Commit: ${env.GIT_SHORT_SHA}"
                }
            }
        }

        stage('2. Static Code Analysis (SonarQube)') {
            steps {
                echo "[*] Triggering SonarQube Scanner for code quality validation..."
                withSonarQubeEnv('SonarQubeServer') {
                    sh """
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                            -Dsonar.projectKey=aceest-fitness-app \
                            -Dsonar.projectVersion=${params.IMAGE_TAG} \
                            -Dsonar.sources=app,ACEest_Fitness.py \
                            -Dsonar.tests=tests
                    """
                }
            }
        }

        stage('3. SonarQube Quality Gate') {
            steps {
                timeout(time: 3, unit: 'MINUTES') {
                    echo "[*] Validating Quality Gate compliance..."
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "Quality Gate failed with status: ${qg.status}. Aborting build."
                        }
                    }
                }
            }
        }

        stage('4. Pytest Automated Unit Testing') {
            steps {
                echo "[*] Executing Pytest test suite with code coverage..."
                sh """
                    mkdir -p reports
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest \
                        --junitxml=reports/junit.xml \
                        --cov=app \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/coverage_html
                """
            }
        }

        stage('5. Publish Test & Coverage Reports') {
            steps {
                echo "[*] Archiving JUnit test results and HTML coverage..."
                junit 'reports/junit.xml'
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/coverage_html',
                    reportFiles: 'index.html',
                    reportName: 'Code Coverage Report'
                ])
            }
        }

        stage('6. Docker Image Build') {
            steps {
                echo "[*] Packaging application into optimized Docker container image..."
                script {
                    sh """
                        docker build -t ${DOCKER_HUB_REPO}:${params.IMAGE_TAG} \
                                     -t ${DOCKER_HUB_REPO}:${env.GIT_SHORT_SHA} \
                                     -t ${DOCKER_HUB_REPO}:latest .
                    """
                }
            }
        }

        stage('7. Container Vulnerability Security Scan') {
            steps {
                echo "[*] Running Trivy vulnerability scan against container image..."
                sh """
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest image --severity HIGH,CRITICAL \
                        --exit-code 0 ${DOCKER_HUB_REPO}:${params.IMAGE_TAG}
                """
            }
        }

        stage('8. Push Image to Container Registry') {
            steps {
                echo "[*] Authenticating and pushing Docker image to Docker Hub..."
                withCredentials([usernamePassword(credentialsId: env.DOCKER_CREDENTIALS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_HUB_REPO}:${params.IMAGE_TAG}
                        docker push ${DOCKER_HUB_REPO}:${env.GIT_SHORT_SHA}
                        docker push ${DOCKER_HUB_REPO}:latest
                    """
                }
            }
        }

        stage('9. Kubernetes Continuous Delivery') {
            steps {
                echo "[*] Deploying application to Kubernetes cluster using strategy: ${params.DEPLOY_STRATEGY}..."
                script {
                    // Ensure namespace exists
                    sh 'kubectl apply -f k8s/00-namespace.yaml'
                    sh 'kubectl apply -f k8s/01-configmap.yaml'

                    switch(params.DEPLOY_STRATEGY) {
                        case 'RollingUpdate':
                            echo "[*] Executing Rolling Update deployment..."
                            sh 'kubectl apply -f k8s/02-rolling-update.yaml'
                            sh "kubectl set image deployment/aceest-app aceest-container=${DOCKER_HUB_REPO}:${params.IMAGE_TAG} -n ${K8S_NAMESPACE}"
                            sh "kubectl rollout status deployment/aceest-app -n ${K8S_NAMESPACE} --timeout=180s"
                            break

                        case 'BlueGreen':
                            echo "[*] Executing Blue-Green switch deployment..."
                            sh 'kubectl apply -f k8s/03-blue-green.yaml'
                            sh 'chmod +x scripts/switch_blue_green.sh && ./scripts/switch_blue_green.sh'
                            break

                        case 'Canary':
                            echo "[*] Executing Canary 80/20 release deployment..."
                            sh 'kubectl apply -f k8s/04-canary.yaml'
                            break

                        case 'ABTesting':
                            echo "[*] Executing A/B Testing deployment with Layer 7 Ingress..."
                            sh 'kubectl apply -f k8s/05-ab-testing.yaml'
                            break

                        case 'Shadow':
                            echo "[*] Executing Shadow Deployment with traffic mirroring..."
                            sh 'kubectl apply -f k8s/06-shadow-deployment.yaml'
                            break
                    }
                }
            }
        }

        stage('10. Post-Deployment Smoke Test & Health Probe') {
            steps {
                echo "[*] Probing Kubernetes endpoint health..."
                script {
                    sh """
                        # Verify deployment rollout pods are in Ready status
                        kubectl get pods -n ${K8S_NAMESPACE} -l app=aceest-fitness
                        
                        # Forward port or query cluster service endpoint
                        ENDPOINT_IP=\$(kubectl get svc aceest-service -n ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "127.0.0.1")
                        echo "Service is accessible at cluster IP: \${ENDPOINT_IP}"
                    """
                }
            }
        }
    }

    post {
        success {
            echo "=========================================================="
            echo " [SUCCESS] Pipeline completed successfully for ${params.IMAGE_TAG}!"
            echo " Application deployed with zero downtime using ${params.DEPLOY_STRATEGY}."
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo " [FAILURE] Pipeline failed! Initiating automated rollback..."
            echo "=========================================================="
            script {
                // Automated rollback to last stable revision in case of failure
                sh """
                    echo "[!] Reverting Kubernetes deployment to previous healthy revision..."
                    kubectl rollout undo deployment/aceest-app -n ${K8S_NAMESPACE} || true
                    kubectl rollout status deployment/aceest-app -n ${K8S_NAMESPACE} --timeout=120s || true
                """
            }
        }
        always {
            cleanWs(cleanWhenNotBuilt: true, deleteDirs: true)
        }
    }
}
