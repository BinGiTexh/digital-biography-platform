# BingiTech Digital Biography Platform

AI-powered content creation platform for building authentic digital presence and thought leadership.

> Agentic Base workflow for digital brand management and portfolio development

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 22+
- OpenAI API Key
- Twitter/X API credentials

### 1. Get Twitter/X API Keys

To get Twitter/X API keys for BingiTech:

1. Go to [developer.twitter.com](https://developer.twitter.com/)
2. Sign in with your BingiTech Twitter account
3. Apply for a developer account (usually approved within 24-48 hours)
4. Create a new app called "BingiTech Content Platform"
5. Generate the following credentials:
   - API Key
   - API Secret Key
   - Bearer Token
   - Access Token
   - Access Token Secret

### 2. Setup Environment

```bash
# Clone and setup
git clone https://github.com/BinGiTexh/digital-biography-platform.git
cd digital-biography-platform

# Copy environment template
cp .env.template .env

# Edit .env with your API keys
nano .env
```

### 3. Start Development Environment

```bash
# Setup development environment
make setup

# Start all services (uses ports 3001, 5433, 6380 to avoid conflicts)
make dev
```

### 4. Generate Your First Content

```bash
# Generate BingiTech content
make generate-content

# Test Twitter posting (will create draft posts first)
make test-twitter
```

## 🏗️ Architecture

- **API Service**: Node.js v22/Express on port 3001
- **Agent System**: Python-based AI agents
- **Database**: PostgreSQL on port 5433
- **Cache**: Redis on port 6380
- **Frontend**: Optional React dashboard

## 📁 Project Structure

```
bingitech-digital-biography/
├── agents/                 # AI agents for content generation
│   ├── core/              # Core agent functionality
│   ├── specialized/       # BingiTech-specific agents
│   └── utils/             # Utility functions
├── clients/bingitech/     # BingiTech-specific configuration
│   ├── config/           # Brand configuration
│   ├── content/          # Generated content
│   └── visuals/          # Visual assets
├── infrastructure/        # Docker & Terraform
├── src/                  # API server code
└── scripts/              # Development & deployment scripts
```

## 🛠️ Available Commands

```bash
make help              # Show all available commands
make setup             # Set up development environment
make dev               # Start development services
make generate-content  # Generate BingiTech content
make test-twitter      # Test Twitter integration
make deploy            # Deploy to production
make clean             # Clean up development environment
```

## 🔧 Configuration

### BingiTech Brand Configuration

Edit `clients/bingitech/config/brand_config.json` to customize:
- Content strategy
- Brand voice and tone
- Content pillars
- Posting schedule
- Visual brand guidelines

### Environment Variables

Key environment variables in `.env`:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TWITTER_*`: Twitter/X API credentials
- `BINGITECH_*`: BingiTech-specific settings

## 📝 Content Strategy

The platform generates content that:
1. Builds thought leadership authentically
2. Showcases technical expertise humbly
3. Engages with the tech community
4. Documents learning and growth

## 🚢 Deployment

### Local Development
Uses Docker Compose with custom ports to avoid conflicts with other projects.

### Production
Deploys to AWS ECS with Terraform infrastructure as code.

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/agents/
npm test --prefix src/
```

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Agent Development Guide](docs/agents.md)
- [Deployment Guide](docs/deployment.md)
- [Content Strategy Guide](docs/content-strategy.md)

## 🔒 Security

- API keys stored in environment variables
- Content encrypted at rest
- No sensitive data in version control
- Regular security updates

## 💰 Cost Tracking

Automated AI cost tracking with Discord notifications:

```bash
# Manual cost logging
python utils/cost_tracker.py log "Service" "operation" 1.50

# Auto-log Ideogram costs
python utils/cost_tracker.py auto-ideogram 4 QUALITY

# Auto-log Cascade costs  
python utils/cost_tracker.py auto-cascade session

# Generate daily report
python utils/cost_tracker.py report
```

**GitHub Action**: Runs daily at 5 PM UTC, sends cost reports to Discord.

**Environment**: Add `DISCORD_COST_WEBHOOK_URL` to `.env` for Discord integration.

## 📞 Support

For BingiTech team support:
- Internal Slack: #digital-biography-platform
- Documentation: `/docs`
- Issues: GitHub Issues
