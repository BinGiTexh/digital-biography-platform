.PHONY: help setup dev clean test lint deploy

# Default target
help:
	@echo "BingiTech Digital Biography Platform - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  setup             - Set up development environment"
	@echo "  dev               - Start development environment (ports: 3001, 5433, 6380)"
	@echo "  test              - Run all tests"
	@echo "  lint              - Run linting"
	@echo "  generate-content  - Generate BingiTech content"
	@echo "  generate-visuals  - Generate AI visual content"
	@echo "  generate-github   - Generate GitHub-based content"
	@echo "  generate-ai       - Generate ALL AI-powered content"
	@echo "  portfolio-sync    - Sync portfolio images from Jetson"
	@echo "  portfolio-post    - Generate CoralScapes tweet drafts"
	@echo "  review-portfolio  - Preview drafts for CoralScapes"
	@echo "  publish-portfolio - Post CoralScapes tweets (test mode)"
	@echo "  test-twitter      - Test Twitter integration"
	@echo "  review-discord    - Send all drafts to Discord for review"
	@echo "  review-twitter    - Send Twitter drafts to Discord"
	@echo "  deploy            - Deploy to production"
	@echo "  clean             - Clean up development environment"
	@echo "  logs              - Show container logs"
	@echo "  db-shell          - Connect to database shell"
	@echo "  redis-shell       - Connect to Redis shell"
	@echo ""

# Development setup
setup:
	@echo "🚀 Setting up BingiTech Digital Biography Platform..."
	@chmod +x scripts/development/setup.sh
	@./scripts/development/setup.sh

# Start development environment
dev:
	@echo "🔧 Starting development environment..."
	@echo "Services will be available on:"
	@echo "  - API: http://localhost:3001"
	@echo "  - Database: localhost:5433"
	@echo "  - Redis: localhost:6380"
	@docker-compose up --build

# Start in background
dev-bg:
	@echo "🔧 Starting development environment in background..."
	@docker-compose up --build -d

# Stop development environment
stop:
	@echo "🛑 Stopping development environment..."
	@docker-compose down

# Run tests
test:
	@echo "🧪 Running tests..."
	@python -m pytest tests/
	@docker-compose exec api npm test

# Run linting
lint:
	@echo "🔍 Running linting..."
	@flake8 agents/
	@black agents/ --check
	@docker-compose exec api npm run lint

# Format code
format:
	@echo "✨ Formatting code..."
	@black agents/
	@docker-compose exec api npm run format

# Deploy to production
deploy:
	@echo "🚀 Deploying to production..."
	@./scripts/deployment/deploy-ecs.sh production

# Clean up development environment
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@docker system prune -f

# Content generation
generate-content:
	@echo "📝 Generating BingiTech content..."
	@python agents/bingitech_agent_system.py

# Test Twitter integration
test-twitter:
	@echo "🐦 Testing Twitter integration..."
	@python agents/specialized/twitter_agent.py --test

# Send drafts to Discord for review
review-discord:
	@echo "🎮 Sending drafts to Discord for review..."
	@python agents/specialized/discord_agent.py

# Send only Twitter drafts to Discord
review-twitter:
	@echo "🐦 Sending Twitter drafts to Discord..."
	@python agents/specialized/discord_agent.py --platform twitter

# Generate AI visual content with Jamaican themes
generate-visuals:
	@echo "🎨 Generating AI visual content..."
	@python agents/specialized/ai_visual_agent.py

# Generate GitHub-based content
generate-github:
	@echo "🐙 Generating GitHub-based content..."
	@python agents/specialized/github_agent.py

# CoralScapes portfolio -------------------------------------------------
portfolio-sync:
	@echo "🔄 Syncing portfolio images from Jetson..."
	@bash scripts/jetson/sync_portfolio.sh

portfolio-post:
	@echo "📝 Generating CoralScapes tweet drafts..."
	@python agents/specialized/coralscapes_portfolio_agent.py

review-portfolio:
	@echo "🎮 Previewing CoralScapes drafts in test Twitter agent..."
	@python agents/specialized/coralscapes_portfolio_agent.py --post

publish-portfolio:
	@echo "🐦 Publishing CoralScapes tweets (requires API creds)..."
	@python agents/specialized/twitter_agent.py --post

# Generate all AI-powered content
generate-ai:
	@echo "🤖 Generating all AI-powered content..."
	@python agents/bingitech_agent_system.py
	@python agents/specialized/ai_visual_agent.py
	@python agents/specialized/github_agent.py

# Show logs
logs:
	@docker-compose logs -f

# Show API logs only
logs-api:
	@docker-compose logs -f api

# Show agent logs only
logs-agents:
	@docker-compose logs -f agents

# Database shell
db-shell:
	@echo "🗃️ Connecting to database..."
	@docker-compose exec postgres psql -U postgres -d bingitech_dev

# Redis shell
redis-shell:
	@echo "📦 Connecting to Redis..."
	@docker-compose exec redis redis-cli

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	@npm install
	@pip install -r requirements.txt

# Update dependencies
update:
	@echo "🔄 Updating dependencies..."
	@npm update
	@pip install -r requirements.txt --upgrade

# Infrastructure
deploy-infrastructure:
	@cd infrastructure/terraform && terraform apply

# Backup database
backup-db:
	@echo "💾 Backing up database..."
	@docker-compose exec postgres pg_dump -U postgres bingitech_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Check health
health:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:3001/health || echo "API not responding"
	@docker-compose ps

# Flux Fine-tuning Commands
flux-setup:
	@echo "🎨 Setting up Flux fine-tuning AWS instance..."
	@./scripts/aws/flux-training-instance.sh launch

flux-status:
	@echo "📊 Checking Flux instance status..."
	@./scripts/aws/flux-training-instance.sh status

flux-ssh:
	@echo "🔗 Connecting to Flux instance..."
	@./scripts/aws/flux-training-instance.sh ssh

flux-terminate:
	@echo "🛑 Terminating Flux instance..."
	@./scripts/aws/flux-training-instance.sh terminate

flux-prepare:
	@echo "🎯 Preparing Flux custom training workflow..."
	@python agents/specialized/flux_custom_agent.py

flux-generate:
	@echo "🎨 Generating with custom Flux model..."
	@python -c "from agents.specialized.flux_custom_agent import FluxCustomAgent; agent = FluxCustomAgent(); agent.run_generation_demo()"

lora-list:
	@echo "📋 Listing available LoRA models..."
	@python -c "from agents.specialized.flux_lora_agent import FluxLoRAAgent; agent = FluxLoRAAgent(); agent.list_available_models()"

lora-generate:
	@echo "🌴 Generating with LoRA outdoor model..."
	@python agents/specialized/flux_lora_agent.py

lora-download:
	@echo "📥 Downloading LoRA models from S3..."
	@python -c "from agents.specialized.flux_lora_agent import FluxLoRAAgent; agent = FluxLoRAAgent(); agent.download_lora_model('outdoor_flux')"

