#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Store PIDs for background processes
STREAMLIT_PID_FILE=".streamlit.pid"
UVICORN_PID_FILE=".uvicorn.pid"

# Print help message
print_help() {
    echo -e "${BLUE}Clinical Agents CLI${NC}"
    echo
    echo "Usage: ./cli.sh [command]"
    echo
    echo "Commands:"
    echo "  install     - Install dependencies and set up virtual environment"
    echo "  start-all   - Start both UI and API server in parallel"
    echo "  start-ui    - Start only the Streamlit UI"
    echo "  start-server- Start only the FastAPI server"
    echo "  stop        - Stop all running services"
    echo "  status      - Check status of running services"
    echo "  db          - Start PostgreSQL database service"
    echo "  db:stop     - Stop PostgreSQL database service"
    echo "  db:create   - Create the database"
    echo "  env         - Set up environment variables"
    echo "  clean       - Remove virtual environment and cached files"
    echo "  help        - Show this help message"
}

# Setup environment variables
setup_env() {
    echo -e "${BLUE}🔐 Setting up environment variables...${NC}"
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file already exists${NC}"
        read -p "Do you want to reconfigure it? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    # Create .env file
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    
    # Google API Key
    read -p "Enter your Google API Key: " google_api_key
    
    # Create or update .env file
    cat > .env << EOL
# Google API Configuration
GOOGLE_API_KEY=${google_api_key}

# Database Configuration
DATABASE_URL=postgresql://localhost/clinical_agents

# Application Configuration
DEBUG=False
ENVIRONMENT=development
EOL

    echo -e "${GREEN}✅ Environment variables configured!${NC}"
    echo -e "${YELLOW}ℹ️  Make sure to keep your .env file secure and never commit it to version control${NC}"
}

# Check environment variables
check_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  No .env file found${NC}"
        read -p "Would you like to set up environment variables now? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            setup_env
        else
            echo -e "${RED}❌ Environment setup skipped. Some features may not work properly.${NC}"
        fi
    fi
}

# Function to check if a process is running
is_process_running() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0  # Process is running
    else
        return 1  # Process is not running
    fi
}

# Function to start a process in background and save its PID
start_process() {
    local command=$1
    local pid_file=$2
    local name=$3
    
    # Check if process is already running
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if is_process_running "$pid"; then
            echo -e "${YELLOW}⚠️  $name is already running (PID: $pid)${NC}"
            return
        else
            rm "$pid_file"
        fi
    fi

    # Start the process in background
    eval "$command" &
    local pid=$!
    echo $pid > "$pid_file"
    echo -e "${GREEN}✅ Started $name (PID: $pid)${NC}"
}

# Function to stop a process
stop_process() {
    local pid_file=$1
    local name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if is_process_running "$pid"; then
            kill "$pid"
            echo -e "${GREEN}✅ Stopped $name (PID: $pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  $name was not running${NC}"
        fi
        rm "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No $name process found${NC}"
    fi
}

# Check and install PostgreSQL
setup_postgres() {
    echo -e "${BLUE}📦 Setting up PostgreSQL...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! brew list postgresql@14 &>/dev/null; then
            echo "Installing PostgreSQL..."
            brew install postgresql@14
        fi
        
        # Add PostgreSQL binaries to PATH if not already there
        if ! echo $PATH | grep -q "/usr/local/opt/postgresql@14/bin"; then
            echo 'export PATH="/usr/local/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
            export PATH="/usr/local/opt/postgresql@14/bin:$PATH"
        fi
    else
        echo -e "${YELLOW}⚠️  Non-macOS system detected. Please install PostgreSQL manually.${NC}"
    fi
}

# Install dependencies and set up environment
install() {
    echo -e "${BLUE}🚀 Setting up Clinical Agents development environment...${NC}"

    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed. Please install Python 3 and try again.${NC}"
        exit 1
    fi

    # Check if Homebrew is installed (for macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
    fi

    # Setup PostgreSQL
    setup_postgres

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo -e "${BLUE}🔌 Activating virtual environment...${NC}"
    source venv/bin/activate

    # Upgrade pip
    echo -e "${BLUE}⬆️  Upgrading pip...${NC}"
    pip install --upgrade pip

    # Remove conflicting packages
    pip uninstall -qqy kfp jupyterlab libpysal thinc spacy fastai ydata-profiling google-cloud-bigquery google-generativeai

    # Install Python packages
    echo -e "${BLUE}📚 Installing Python dependencies...${NC}"
    pip install -r requirements.txt

    # Setup environment variables
    check_env

    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo -e "${YELLOW}ℹ️  Don't forget to start the database with: ./cli.sh db${NC}"
}

# Start the database
start_db() {
    echo -e "${BLUE}🚀 Starting PostgreSQL database...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@14
        echo -e "${GREEN}✅ PostgreSQL started!${NC}"
    else
        echo -e "${YELLOW}⚠️  Please start PostgreSQL using your system's service manager${NC}"
    fi
}

# Stop the database
stop_db() {
    echo -e "${BLUE}🛑 Stopping PostgreSQL database...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services stop postgresql@14
        echo -e "${GREEN}✅ PostgreSQL stopped!${NC}"
    else
        echo -e "${YELLOW}⚠️  Please stop PostgreSQL using your system's service manager${NC}"
    fi
}

# Create the database
create_db() {
    echo -e "${BLUE}🗄️  Creating database...${NC}"
    if ! command -v createdb &> /dev/null; then
        echo -e "${RED}❌ PostgreSQL commands not found. Is PostgreSQL installed?${NC}"
        exit 1
    fi

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    until pg_isready 2>/dev/null; do
        sleep 1
    done

    if ! psql -lqt | cut -d \| -f 1 | grep -qw "clinical_agents"; then
        createdb clinical_agents
        echo -e "${GREEN}✅ Database 'clinical_agents' created!${NC}"
    else
        echo -e "${YELLOW}ℹ️  Database 'clinical_agents' already exists${NC}"
    fi
}

# Start the UI
start_ui() {
    echo -e "${BLUE}🚀 Starting UI...${NC}"
    check_env
    source venv/bin/activate
    start_process "streamlit run app/streamlit_app.py" "$STREAMLIT_PID_FILE" "Streamlit UI"
}

# Start the server
start() {
    if [ ! -d "venv" ]; then
        echo -e "${RED}❌ Virtual environment not found. Please run './cli.sh install' first.${NC}"
        exit 1
    fi

    # Check if PostgreSQL is running
    if ! pg_isready &>/dev/null; then
        echo -e "${YELLOW}⚠️  PostgreSQL is not running. Starting it now...${NC}"
        start_db
        sleep 3  # Give PostgreSQL time to start
    fi

    check_env
    echo -e "${BLUE}🚀 Starting FastAPI server...${NC}"
    source venv/bin/activate
    start_process "uvicorn app.main:app --reload" "$UVICORN_PID_FILE" "FastAPI Server"
}

# Start all services
start_all() {
    echo -e "${BLUE}🚀 Starting All Services...${NC}"
    source venv/bin/activate
    check_env
    start_ui
    start
}

# Stop all services
stop_all() {
    echo -e "${BLUE}🛑 Stopping all services...${NC}"
    stop_process "$STREAMLIT_PID_FILE" "Streamlit UI"
    stop_process "$UVICORN_PID_FILE" "FastAPI Server"
}

# Check status of services
check_status() {
    echo -e "${BLUE}📊 Checking service status...${NC}"
    
    # Check environment
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ Environment file exists${NC}"
    else
        echo -e "${RED}❌ Environment file missing${NC}"
    fi
    
    # Check Streamlit
    if [ -f "$STREAMLIT_PID_FILE" ]; then
        local pid=$(cat "$STREAMLIT_PID_FILE")
        if is_process_running "$pid"; then
            echo -e "${GREEN}✅ Streamlit UI is running (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ Streamlit UI is not running${NC}"
            rm "$STREAMLIT_PID_FILE"
        fi
    else
        echo -e "${YELLOW}ℹ️  Streamlit UI is not running${NC}"
    fi
    
    # Check FastAPI
    if [ -f "$UVICORN_PID_FILE" ]; then
        local pid=$(cat "$UVICORN_PID_FILE")
        if is_process_running "$pid"; then
            echo -e "${GREEN}✅ FastAPI Server is running (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ FastAPI Server is not running${NC}"
            rm "$UVICORN_PID_FILE"
        fi
    else
        echo -e "${YELLOW}ℹ️  FastAPI Server is not running${NC}"
    fi
    
    # Check PostgreSQL
    if pg_isready &>/dev/null; then
        echo -e "${GREEN}✅ PostgreSQL is running${NC}"
    else
        echo -e "${RED}❌ PostgreSQL is not running${NC}"
    fi
}

# Clean up virtual environment and cached files
clean() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    # Remove virtual environment
    if [ -d "venv" ]; then
        echo "Removing virtual environment..."
        rm -rf venv
    fi

    # Remove Python cache files
    echo "Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -r {} +
    find . -type f -name "*.pyc" -delete

    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Main command router
case "$1" in
    "install")
        install
        ;;
    "start-all")
        start_all
        ;;
    "start-ui")
        start_ui
        ;;
    "start-server")
        start
        ;;
    "stop")
        stop_all
        ;;
    "status")
        check_status
        ;;
    "env")
        setup_env
        ;;
    "db")
        start_db
        ;;
    "db:stop")
        stop_db
        ;;
    "db:create")
        create_db
        ;;
    "clean")
        clean
        ;;
    "help"|"")
        print_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run './cli.sh help' for usage information"
        exit 1
        ;;
esac 