#!/usr/bin/env python3
"""
Dashboard Deployment Selector

Interactive CLI tool to deploy the P2P dashboard to various platforms.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def check_command(command):
    """Check if a command is available"""
    return shutil.which(command) is not None


def run_command(command, shell=False):
    """Run a shell command and return success status"""
    try:
        if shell:
            subprocess.run(command, shell=True, check=True)
        else:
            subprocess.run(command.split(), check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        return False


def deploy_github_pages():
    """Deploy to GitHub Pages"""
    print_header("GitHub Pages Deployment")

    print_info("This is the default and FREE option!")
    print_info("Dashboard updates automatically via GitHub Actions workflow.")

    print("\nSteps to enable:")
    print("1. Go to your repository Settings")
    print("2. Navigate to Pages section")
    print("3. Source: Select 'gh-pages' branch")
    print("4. Save")
    print("")

    confirm = input(f"{Colors.OKGREEN}Would you like to open GitHub Pages settings? (y/n): {Colors.ENDC}")

    if confirm.lower() == 'y':
        repo_url = subprocess.check_output(
            ['git', 'remote', 'get-url', 'origin'],
            text=True
        ).strip()

        # Convert git URL to HTTP URL
        if repo_url.startswith('git@'):
            repo_url = repo_url.replace(':', '/').replace('git@', 'https://')
        repo_url = repo_url.replace('.git', '')

        settings_url = f"{repo_url}/settings/pages"

        print_info(f"Opening: {settings_url}")

        if sys.platform == 'darwin':
            run_command(f'open {settings_url}', shell=True)
        elif sys.platform == 'linux':
            run_command(f'xdg-open {settings_url}', shell=True)
        else:
            print(f"\nPlease visit: {settings_url}")

    print_success("GitHub Pages setup instructions displayed!")
    print_info("Dashboard will be available at: https://<username>.github.io/<repo>/")


def deploy_cloud_run():
    """Deploy to Google Cloud Run"""
    print_header("Cloud Run Deployment")

    # Check prerequisites
    if not check_command('gcloud'):
        print_error("gcloud CLI not found!")
        print_info("Install from: https://cloud.google.com/sdk/docs/install")
        return

    if not check_command('docker'):
        print_error("Docker not found!")
        print_info("Install from: https://docs.docker.com/get-docker/")
        return

    # Get configuration
    print_info("Please provide the following information:")

    project_id = input("GCP Project ID: ")
    region = input("Region (default: asia-northeast1): ") or "asia-northeast1"
    service_name = input("Service name (default: p2p-dashboard): ") or "p2p-dashboard"
    github_token = input("GitHub Token: ")
    github_repo = input("GitHub Repository (user/repo): ")

    # Build image
    print("\n📦 Building Docker image...")
    image_name = f"gcr.io/{project_id}/{service_name}"

    os.chdir('deployments/cloudrun')

    if not run_command(f"docker build -t {image_name} .", shell=True):
        print_error("Docker build failed!")
        return

    print_success("Docker image built!")

    # Push to registry
    print("\n☁️  Pushing to Container Registry...")

    if not run_command(f"docker push {image_name}", shell=True):
        print_error("Docker push failed!")
        return

    print_success("Image pushed to registry!")

    # Deploy to Cloud Run
    print("\n🚀 Deploying to Cloud Run...")

    deploy_cmd = (
        f"gcloud run deploy {service_name} "
        f"--image {image_name} "
        f"--platform managed "
        f"--region {region} "
        f"--allow-unauthenticated "
        f"--set-env-vars GITHUB_TOKEN={github_token},GITHUB_REPO={github_repo} "
        f"--project {project_id}"
    )

    if not run_command(deploy_cmd, shell=True):
        print_error("Cloud Run deployment failed!")
        return

    print_success("Deployed to Cloud Run!")

    # Get service URL
    url_cmd = f"gcloud run services describe {service_name} --region {region} --format 'value(status.url)' --project {project_id}"
    service_url = subprocess.check_output(url_cmd, shell=True, text=True).strip()

    print("\n" + "="*60)
    print_success(f"Dashboard URL: {service_url}")
    print("="*60)


def deploy_vps():
    """Deploy to VPS"""
    print_header("VPS Deployment")

    print_info("This will create a docker-compose.yml file for easy VPS deployment.")

    # Get configuration
    github_token = input("GitHub Token: ")
    github_repo = input("GitHub Repository (user/repo): ")
    port = input("Port (default: 80): ") or "80"

    # Create docker-compose.yml
    docker_compose = f"""version: '3'

services:
  dashboard:
    image: ghcr.io/autonomous-dev/p2p-dashboard:latest
    ports:
      - "{port}:8080"
    environment:
      - GITHUB_TOKEN={github_token}
      - GITHUB_REPO={github_repo}
    restart: always

  # Optional: Add Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    restart: always

  # Optional: Add Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
"""

    # Save file
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)

    print_success("Created docker-compose.yml")

    print("\n📋 Deployment Instructions:")
    print("="*60)
    print("1. Copy docker-compose.yml to your VPS:")
    print(f"   scp docker-compose.yml root@YOUR_VPS_IP:/root/")
    print("")
    print("2. SSH to your VPS:")
    print("   ssh root@YOUR_VPS_IP")
    print("")
    print("3. Install Docker (if not already):")
    print("   curl -fsSL https://get.docker.com | sh")
    print("")
    print("4. Start services:")
    print("   docker-compose up -d")
    print("")
    print("5. Access dashboard:")
    print(f"   http://YOUR_VPS_IP:{port}")
    print("="*60)

    print_success("VPS deployment files created!")


def deploy_lambda():
    """Deploy to AWS Lambda"""
    print_header("AWS Lambda Deployment")

    # Check prerequisites
    if not check_command('serverless'):
        print_error("Serverless Framework not found!")
        print_info("Install with: npm install -g serverless")
        return

    print_info("Creating Serverless configuration...")

    # Create serverless.yml
    serverless_config = """service: p2p-dashboard

provider:
  name: aws
  runtime: python3.11
  region: ap-northeast-1
  environment:
    GITHUB_TOKEN: ${env:GITHUB_TOKEN}
    GITHUB_REPO: ${env:GITHUB_REPO}

functions:
  dashboard:
    handler: handler.dashboard
    events:
      - http:
          path: /
          method: ANY
      - http:
          path: /{proxy+}
          method: ANY

  api:
    handler: handler.api
    events:
      - http:
          path: /api/{proxy+}
          method: ANY

plugins:
  - serverless-python-requirements
  - serverless-wsgi

custom:
  wsgi:
    app: server.app
  pythonRequirements:
    dockerizePip: true
"""

    os.makedirs('deployments/lambda', exist_ok=True)

    with open('deployments/lambda/serverless.yml', 'w') as f:
        f.write(serverless_config)

    print_success("Created serverless.yml")

    # Get environment variables
    github_token = input("GitHub Token: ")
    github_repo = input("GitHub Repository (user/repo): ")

    # Set environment variables
    os.environ['GITHUB_TOKEN'] = github_token
    os.environ['GITHUB_REPO'] = github_repo

    print("\n🚀 Deploying to AWS Lambda...")
    os.chdir('deployments/lambda')

    if not run_command("serverless deploy", shell=True):
        print_error("Lambda deployment failed!")
        return

    print_success("Deployed to AWS Lambda!")


def main():
    """Main function"""
    print_header("P2P Dashboard Deployment Tool")

    print("Select deployment option:\n")
    print(f"{Colors.OKGREEN}1. GitHub Pages (FREE, Default)      Cost: $0/month{Colors.ENDC}")
    print(f"{Colors.OKCYAN}2. Google Cloud Run                  Cost: $0-10/month{Colors.ENDC}")
    print(f"{Colors.OKBLUE}3. VPS (Sakura, DigitalOcean, etc.)  Cost: $4-25/month{Colors.ENDC}")
    print(f"{Colors.WARNING}4. AWS Lambda                        Cost: $0-5/month{Colors.ENDC}")
    print("")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        deploy_github_pages()
    elif choice == '2':
        deploy_cloud_run()
    elif choice == '3':
        deploy_vps()
    elif choice == '4':
        deploy_lambda()
    else:
        print_error("Invalid choice!")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)
