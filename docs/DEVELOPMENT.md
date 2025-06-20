# BingiTech Digital Biography Platform - Development Guide

## 🚀 Getting Started

### Quick Setup

1. **Clone and Initialize**
   ```bash
   git clone <repository-url>
   cd bingitech-digital-biography
   make setup
   ```

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

3. **Start Development**
   ```bash
   make dev
   ```

## 🏗️ Architecture Overview

### Services and Ports

| Service    | Port | Description                    |
|------------|------|--------------------------------|
| API Server | 3001 | Node.js Express API            |
| Database   | 5433 | PostgreSQL (custom port)      |
| Redis      | 6380 | Redis cache (custom port)     |

*Custom ports prevent conflicts with other local projects*

### Directory Structure

```
bingitech-digital-biography/
├── agents/                    # AI agents (Python)
│   ├── bingitech_agent_system.py    # Main agent orchestrator
│   ├── specialized/           # Platform-specific agents
│   │   └── twitter_agent.py   # Twitter/X integration
│   └── utils/                 # Shared utilities
├── clients/bingitech/         # BingiTech configuration
│   ├── config/               # Brand and strategy config
│   └── content/              # Generated content
├── src/                      # API server (Node.js)
│   └── server.js             # Express server
├── infrastructure/           # Docker & Terraform
│   ├── docker/               # Dockerfiles
│   └── terraform/            # Infrastructure as code
└── scripts/                  # Development scripts
    ├── development/          # Local dev scripts
    └── deployment/           # Production deployment
```

## 🛠️ Development Commands

### Environment Management

```bash
make setup          # Initial setup
make dev            # Start all services
make dev-bg         # Start in background
make stop           # Stop all services
make clean          # Clean up containers
```

### Content Generation

```bash
make generate-content    # Generate BingiTech content
make test-twitter       # Test Twitter integration
```

### Development Tools

```bash
make logs              # View all container logs
make logs-api          # View API logs only
make logs-agents       # View agent logs only
make db-shell          # Connect to database
make redis-shell       # Connect to Redis
```

### Code Quality

```bash
make test              # Run all tests
make lint              # Run linting
make format            # Format code
```

## 🔧 Configuration

### Environment Variables (.env)

**Required for Development:**
- `OPENAI_API_KEY` - OpenAI API key for content generation
- `NODE_ENV=development`
- `PORT=3001`

**Required for Twitter Integration:**
- `X_API_KEY` - Twitter API key
- `X_API_SECRET` - Twitter API secret
- `X_BEARER_TOKEN` - Twitter bearer token
- `X_ACCESS_TOKEN` - Twitter access token
- `X_ACCESS_TOKEN_SECRET` - Twitter access token secret

**Optional:**
- `AWS_*` - AWS credentials (for deployment)
- `SENTRY_DSN` - Error tracking
- `DATADOG_API_KEY` - Monitoring

### Brand Configuration

Edit `clients/bingitech/config/brand_config.json` to customize:

- **Content Strategy**: Voice, tone, perspective
- **Content Pillars**: Focus areas for content
- **Platform Settings**: Posting schedules and frequency
- **Target Audience**: Demographics and interests
- **Visual Brand**: Colors, typography, style

## 📝 Content Generation Workflow

### 1. Generate Content

```bash
make generate-content
```

This creates draft posts in `clients/bingitech/content/generated/`

### 2. Review Content

Generated content includes:
- Twitter posts (280 characters max)
- LinkedIn posts (longer form)
- Content metadata (pillar, timestamp, etc.)

### 3. Test Social Media Integration

```bash
make test-twitter
```

This runs in test mode by default - no actual posting occurs.

### 4. Manual Review and Editing

- Edit generated content files as needed
- Approve content before posting
- Update brand configuration based on performance

## 🧪 Testing

### Content Generation Testing

```bash
# Test agent system
python agents/bingitech_agent_system.py

# Test specific agents
python agents/specialized/twitter_agent.py --test
```

### API Testing

```bash
# Health check
curl http://localhost:3001/health

# API status
curl http://localhost:3001/api/status

# Agent status
curl http://localhost:3001/api/agents/status
```

### Database Testing

```bash
# Connect to database
make db-shell

# Run in container
psql -U postgres -d bingitech_dev
```

## 🐛 Troubleshooting

### Common Issues

**Port Conflicts:**
- Services use custom ports (3001, 5433, 6380)
- Check if ports are available: `lsof -i :3001`

**Docker Issues:**
```bash
# Restart Docker
make clean
make dev

# Check container status
docker-compose ps

# View container logs
make logs
```

**Environment Issues:**
```bash
# Verify environment
source .env
echo $OPENAI_API_KEY

# Check Node.js version
node --version  # Should be v22+
```

**Content Generation Issues:**
```bash
# Check agent configuration
python agents/bingitech_agent_system.py

# Verify brand config
cat clients/bingitech/config/brand_config.json | jq
```

### Log Locations

- Container logs: `docker-compose logs`
- Application logs: `logs/` directory
- Content output: `clients/bingitech/content/generated/`

## 🚢 Deployment

### Local Development

Uses Docker Compose with:
- Hot reloading for Node.js (nodemon)
- Volume mounts for Python agents
- Persistent data volumes

### Production Deployment

```bash
# Deploy infrastructure
make deploy-infrastructure

# Deploy application
make deploy
```

## 🔄 Development Workflow

### Daily Development

1. **Start Environment**
   ```bash
   make dev-bg
   ```

2. **Generate and Test Content**
   ```bash
   make generate-content
   make test-twitter
   ```

3. **Monitor Logs**
   ```bash
   make logs-agents
   ```

4. **Stop When Done**
   ```bash
   make stop
   ```

### Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-content-pillar
   ```

2. **Update Configuration**
   - Modify `clients/bingitech/config/brand_config.json`
   - Add new content templates
   - Update agent logic

3. **Test Changes**
   ```bash
   make test
   make generate-content
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add new content pillar"
   git push origin feature/new-content-pillar
   ```

## 📊 Monitoring and Analytics

### Health Monitoring

- Health endpoint: `http://localhost:3001/health`
- Agent status: `http://localhost:3001/api/agents/status`
- Container health: `docker-compose ps`

### Content Performance

- Review generated content in `clients/bingitech/content/generated/`
- Track posting success rates
- Monitor engagement metrics (manual for now)

## 🔒 Security

### Development Security

- API keys in environment variables only
- No secrets in version control
- Content encryption for sensitive data
- Container security best practices

### Production Security

- Environment-specific configurations
- Secure credential management
- Network security
- Regular security updates

## 📚 Additional Resources

- [API Documentation](api.md)
- [Agent Development Guide](agents.md)
- [Deployment Guide](deployment.md)
- [Content Strategy Guide](content-strategy.md)

