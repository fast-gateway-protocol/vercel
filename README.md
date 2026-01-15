# FGP Vercel Daemon

Fast Vercel operations via FGP daemon. Manage projects, deployments, and logs without MCP cold-start overhead.

## Installation

```bash
git clone https://github.com/fast-gateway-protocol/vercel.git
cd fgp-vercel
cargo build --release
```

**Requirements:**
- Rust 1.70+
- Vercel access token (`VERCEL_TOKEN` env var)

## Quick Start

```bash
# Set your Vercel token
export VERCEL_TOKEN="xxxxx"

# Start the daemon
./target/release/fgp-vercel start

# List projects
fgp call vercel.projects

# Get project details
fgp call vercel.project '{"project_id": "my-project"}'

# List deployments
fgp call vercel.deployments '{"project_id": "my-project", "limit": 5}'

# Get deployment logs
fgp call vercel.logs '{"deployment_id": "dpl_xxxxx"}'

# Stop daemon
./target/release/fgp-vercel stop
```

## Available Methods

| Method | Params | Description |
|--------|--------|-------------|
| `vercel.projects` | `limit` (default: 20) | List all projects |
| `vercel.project` | `project_id` (required) | Get project details |
| `vercel.deployments` | `project_id`, `limit` | List deployments |
| `vercel.deployment` | `deployment_id` (required) | Get deployment details |
| `vercel.logs` | `deployment_id` (required) | Get deployment logs/events |
| `vercel.user` | - | Get current user info |

## FGP Protocol

Socket: `~/.fgp/services/vercel/daemon.sock`

**Request:**
```json
{"id": "uuid", "v": 1, "method": "vercel.deployments", "params": {"project_id": "my-app", "limit": 5}}
```

**Response:**
```json
{"id": "uuid", "ok": true, "result": {"deployments": [...], "count": 5}}
```

## Why FGP?

| Operation | FGP Daemon | MCP stdio | Speedup |
|-----------|------------|-----------|---------|
| List projects | ~200ms | ~2,500ms | **12x** |
| Get logs | ~180ms | ~2,400ms | **13x** |

FGP keeps the API connection warm, eliminating cold-start overhead.

## Use Cases

- **Deployment monitoring**: Quick status checks during CI/CD
- **Log debugging**: Fast access to deployment events
- **Project management**: List and query projects programmatically
- **AI agents**: Integrate deployment status into agent workflows

## Troubleshooting

### Invalid Token

**Symptom:** Requests fail with 401 or "unauthorized"

**Solutions:**
1. Verify token is set: `echo $VERCEL_TOKEN`
2. Check token is valid: `curl -H "Authorization: Bearer $VERCEL_TOKEN" https://api.vercel.com/v2/user`
3. Generate new token at https://vercel.com/account/tokens

### Project Not Found

**Symptom:** "Project not found" for existing project

**Check:**
1. Use project name or ID correctly
2. Token has access to the team/account owning the project
3. List projects first: `fgp call vercel.projects`

### Deployment Not Found

**Symptom:** "Deployment not found" error

**Check:**
1. Deployment ID format: `dpl_xxxxx`
2. Deployment exists and isn't deleted
3. List deployments: `fgp call vercel.deployments '{"project_id": "xxx"}'`

### Empty Logs

**Symptom:** `vercel.logs` returns empty for active deployment

**Note:**
1. Logs may take a few seconds to populate
2. Build logs vs runtime logs are separate
3. Some deployments (static) have minimal logs

### Rate Limiting

**Symptom:** 429 errors or "Too Many Requests"

**Solutions:**
1. Vercel has API rate limits (varies by plan)
2. Add delays between bulk operations
3. Cache project/deployment lists when possible

### Team/Scope Issues

**Symptom:** Can't see team projects

**Check:**
1. Token was created with team scope
2. Use team ID in requests if needed
3. Personal tokens only see personal projects by default

### Connection Refused

**Symptom:** "Connection refused" when calling daemon

**Solution:**
```bash
# Check daemon is running
pgrep -f fgp-vercel

# Restart daemon
./target/release/fgp-vercel stop
export VERCEL_TOKEN="xxxxx"
./target/release/fgp-vercel start

# Verify socket
ls ~/.fgp/services/vercel/daemon.sock
```

### Slow Log Retrieval

**Symptom:** `vercel.logs` takes longer than expected

**Note:**
1. Large deployments have more logs
2. Use `limit` parameter to reduce response size
3. Recent deployments may still be writing logs

## License

MIT
