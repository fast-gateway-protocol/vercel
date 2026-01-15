#!/usr/bin/env python3
"""
Vercel Daemon - Basic Operations Example

Demonstrates common Vercel operations using the FGP Vercel daemon.
Requires:
  - Vercel daemon running (`fgp start vercel`)
  - VERCEL_TOKEN environment variable set
"""

import json
import socket
import uuid
from pathlib import Path

SOCKET_PATH = Path.home() / ".fgp/services/vercel/daemon.sock"


def call_daemon(method: str, params: dict = None) -> dict:
    """Send a request to the Vercel daemon and return the response."""
    request = {
        "id": str(uuid.uuid4()),
        "v": 1,
        "method": method,
        "params": params or {}
    }

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(str(SOCKET_PATH))
        sock.sendall((json.dumps(request) + "\n").encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
            if b"\n" in response:
                break

        return json.loads(response.decode().strip())


def list_projects():
    """List all Vercel projects."""
    print("\n🚀 Vercel Projects")
    print("-" * 40)

    result = call_daemon("vercel.projects", {})

    if result.get("ok"):
        projects = result["result"].get("projects", [])
        if not projects:
            print("  No projects found")
        for project in projects:
            framework = project.get("framework", "unknown")
            print(f"  • {project.get('name')}")
            print(f"    Framework: {framework}")
            print(f"    Updated: {project.get('updatedAt', 'unknown')}")
            print()
    else:
        print(f"  ❌ Error: {result.get('error')}")


def list_deployments(project_name: str = None, limit: int = 5):
    """List recent deployments."""
    target = f"for {project_name}" if project_name else ""
    print(f"\n📦 Recent Deployments {target}")
    print("-" * 40)

    params = {"limit": limit}
    if project_name:
        params["project"] = project_name

    result = call_daemon("vercel.deployments", params)

    if result.get("ok"):
        deployments = result["result"].get("deployments", [])
        if not deployments:
            print("  No deployments found")
        for deploy in deployments:
            state = deploy.get("state", "unknown")
            state_icon = {
                "READY": "🟢",
                "ERROR": "🔴",
                "BUILDING": "🟡",
                "QUEUED": "⚪"
            }.get(state, "⚪")

            print(f"  {state_icon} {deploy.get('url', 'no-url')}")
            print(f"     State: {state}")
            print(f"     Created: {deploy.get('created', 'unknown')}")
            if deploy.get("meta", {}).get("githubCommitMessage"):
                print(f"     Commit: {deploy['meta']['githubCommitMessage'][:50]}...")
            print()
    else:
        print(f"  ❌ Error: {result.get('error')}")


def get_deployment_logs(deployment_id: str, limit: int = 50):
    """Get logs for a specific deployment."""
    print(f"\n📝 Logs for deployment: {deployment_id}")
    print("-" * 40)

    result = call_daemon("vercel.logs", {
        "deployment_id": deployment_id,
        "limit": limit
    })

    if result.get("ok"):
        logs = result["result"].get("logs", [])
        if not logs:
            print("  No logs found")
        for log in logs:
            level = log.get("level", "info")
            level_icon = {"error": "❌", "warn": "⚠️", "info": "ℹ️"}.get(level, "•")
            print(f"  {level_icon} {log.get('message', '')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")


def get_deployment_status(deployment_id: str):
    """Get detailed status for a deployment."""
    print(f"\n📊 Deployment Status: {deployment_id}")
    print("-" * 40)

    result = call_daemon("vercel.status", {"deployment_id": deployment_id})

    if result.get("ok"):
        status = result["result"]
        state = status.get("state", "unknown")
        state_icon = "🟢" if state == "READY" else "🔴" if state == "ERROR" else "🟡"

        print(f"  {state_icon} State: {state}")
        print(f"  URL: {status.get('url')}")
        print(f"  Created: {status.get('created')}")

        if status.get("build"):
            build = status["build"]
            print(f"\n  Build:")
            print(f"    Duration: {build.get('duration', 'unknown')}ms")
            print(f"    Status: {build.get('status')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")


def list_domains(project_name: str):
    """List domains for a project."""
    print(f"\n🌐 Domains for: {project_name}")
    print("-" * 40)

    result = call_daemon("vercel.domains", {"project": project_name})

    if result.get("ok"):
        domains = result["result"].get("domains", [])
        if not domains:
            print("  No domains configured")
        for domain in domains:
            verified = "✓" if domain.get("verified") else "✗"
            print(f"  [{verified}] {domain.get('name')}")
    else:
        print(f"  ❌ Error: {result.get('error')}")


if __name__ == "__main__":
    print("Vercel Daemon Examples")
    print("=" * 40)

    # Check daemon health first
    health = call_daemon("health")
    if not health.get("ok"):
        print("❌ Vercel daemon not running. Start with: fgp start vercel")
        print("   Also ensure VERCEL_TOKEN is set")
        exit(1)

    print("✅ Vercel daemon is healthy")

    # Run examples
    list_projects()
    list_deployments(limit=5)

    # Uncomment with your project/deployment:
    # list_deployments("your-project-name", limit=3)
    # get_deployment_status("dpl_xxxxxxxxxxxx")
    # get_deployment_logs("dpl_xxxxxxxxxxxx")
    # list_domains("your-project-name")
