#!/bin/bash

echo "🚀 BingiTech Digital Biography Platform - Development Setup"
echo "========================================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists brew; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check Node.js version
if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 22 ]; then
        echo "⚠️  Node.js version $NODE_VERSION detected. Installing Node.js v22..."
        brew install node@22
        echo "Please restart your terminal and run this script again."
        exit 1
    else
        echo "✅ Node.js v$NODE_VERSION found"
    fi
else
    echo "📦 Installing Node.js v22..."
    brew install node@22
fi

# Install required tools
echo "🛠️ Installing development tools..."
brew_packages=(
    "git" "docker" "docker-compose" "terraform" 
    "awscli" "python@3.11"
)

for package in "${brew_packages[@]}"; do
    if ! brew list "$package" &>/dev/null; then
        echo "Installing $package..."
        brew install "$package"
    else
        echo "✅ $package already installed"
    fi
done

# Install Python packages
echo "🐍 Installing Python packages..."
if command_exists python3; then
    pip3 install -r requirements.txt
else
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Install Node.js packages
echo "📦 Installing Node.js packages..."
npm install

# Setup environment file
if [ ! -f .env ]; then
    echo "⚙️ Setting up environment configuration..."
    cp .env.template .env
    echo ""
    echo "📝 Please update .env with your API keys:"
    echo "   - OpenAI API Key (https://platform.openai.com/api-keys)"
    echo "   - X (Twitter) API credentials (https://developer.twitter.com/)"
    echo "   - AWS credentials (optional for deployment)"
    echo ""
    echo "Twitter API Setup Instructions:"
    echo "1. Go to https://developer.twitter.com/"
    echo "2. Sign in with your BingiTech Twitter account"
    echo "3. Apply for developer access"
    echo "4. Create a new app called 'BingiTech Content Platform'"
    echo "5. Generate API keys and tokens"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
fi

# Start Docker if not running
if ! docker info &>/dev/null; then
    echo "🐳 Starting Docker..."
    open -a Docker
    echo "⏳ Waiting for Docker to start..."
    while ! docker info &>/dev/null; do
        sleep 5
    done
fi

# Initialize Git repository if needed
if [ ! -d .git ]; then
    echo "🗃️ Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: BingiTech Digital Biography Platform"
fi

# Create necessary directories
echo "📁 Setting up BingiTech workspace..."
mkdir -p clients/bingitech/{content/generated,visuals/generated,infrastructure,assets}
mkdir -p logs

# Test environment
echo "🧪 Testing environment..."
if [ -f .env ]; then
    source .env
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
        echo "⚠️  OpenAI API key not configured in .env"
    else
        echo "✅ OpenAI API key configured"
    fi
fi

echo ""
echo "✅ Setup complete! Your BingiTech development environment is ready."
echo ""
echo "🌐 Custom ports to avoid conflicts:"
echo "   - API Server: http://localhost:3001"
echo "   - PostgreSQL: localhost:5433"
echo "   - Redis: localhost:6380"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env with your actual API keys"
echo "   2. Start development environment: make dev"
echo "   3. Generate first content: make generate-content"
echo "   4. Test Twitter integration: make test-twitter"
echo ""
echo "🛠️ Available commands:"
echo "   make help    - Show all available commands"
echo "   make dev     - Start development environment"
echo "   make logs    - View container logs"
echo "   make clean   - Clean up environment"
echo ""

