#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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
    echo "  test-api    - Test assessment API endpoints"
    echo "  test-users  - Test users API endpoints"
    echo "  help        - Show this help message"
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

    # Install Python packages
    echo -e "${BLUE}📚 Installing Python dependencies...${NC}"
    pip install -r requirements_new.txt

    echo -e "${GREEN}✅ Installation complete!${NC}"
}

# Start the UI
start_ui() {
    echo -e "${BLUE}🚀 Starting UI...${NC}"
    streamlit run app/streamlit_app.py
}

# Start the server
start_server() {
    echo -e "${BLUE}🚀 Starting FastAPI server...${NC}"
    uvicorn app.main:app --reload
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
# Test API endpoints
test_api() {
    echo -e "${BLUE}🧪 Testing API endpoints...${NC}"
    local API_URL="http://localhost:8000/api/v1"
    local USER_ID=4

    # Create a test assessment with user_id=4
    echo -e "\n📝 Creating test assessment..."
    ASSESSMENT_RESPONSE=$(curl -s -X POST "${API_URL}/assessments" \
        -H "Content-Type: application/json" \
        -d "{
            \"notes\": \"Patient presents with severe headache\",
            \"esi_level\": 2,
            \"diagnosis\": \"Migraine\",
            \"user_id\": ${USER_ID}
        }")
    
    echo "$ASSESSMENT_RESPONSE"
    ASSESSMENT_ID=$(echo "$ASSESSMENT_RESPONSE" | jq -r '.id')

    # Get all assessments
    echo -e "\n📋 Getting all assessments..."
    curl -s -X GET "${API_URL}/assessments" | jq

    # Create another test assessment
    echo -e "\n📝 Creating another test assessment..."
    ASSESSMENT_RESPONSE_2=$(curl -s -X POST "${API_URL}/assessments" \
        -H "Content-Type: application/json" \
        -d "{
            \"notes\": \"Patient has chest pain and shortness of breath\",
            \"esi_level\": 1,
            \"diagnosis\": \"Possible MI\",
            \"user_id\": ${USER_ID}
        }")
    
    echo "$ASSESSMENT_RESPONSE_2"
    ASSESSMENT_ID_2=$(echo "$ASSESSMENT_RESPONSE_2" | jq -r '.id')

    # Delete the first assessment
    echo -e "\n🗑️  Deleting assessment ${ASSESSMENT_ID}..."
    curl -s -X DELETE "${API_URL}/assessments/${ASSESSMENT_ID}"

    # Verify deletion by getting all assessments again
    echo -e "\n📋 Getting all assessments after deletion..."
    curl -s -X GET "${API_URL}/assessments" | jq

    echo -e "\n${GREEN}✅ API tests complete!${NC}"
}

# Test Users API endpoints
test_users_api() {
    echo -e "${BLUE}🧪 Testing Users API endpoints...${NC}"
    local API_URL="http://localhost:8000/api/v1"

    # Create/Login a patient user
    echo -e "\n👤 Creating/Login patient user..."
    PATIENT_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "gender": "male",
            "user_type": "patient"
        }')
    
    echo "$PATIENT_RESPONSE"
    PATIENT_ID=$(echo "$PATIENT_RESPONSE" | jq -r '.id')

    # Create/Login a staff user
    echo -e "\n👩‍⚕️ Creating/Login staff user..."
    STAFF_RESPONSE=$(curl -s -X POST "${API_URL}/users/login" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Dr. Jane Smith",
            "email": "jane.smith@hospital.com",
            "age": 35,
            "gender": "female",
            "user_type": "staff"
        }')
    
    echo "$STAFF_RESPONSE"
    STAFF_ID=$(echo "$STAFF_RESPONSE" | jq -r '.id')

    # Get patient user by ID
    echo -e "\n📋 Getting patient user by ID ($PATIENT_ID)..."
    curl -s -X GET "${API_URL}/users/${PATIENT_ID}" | jq

    # Get staff user by ID
    echo -e "\n📋 Getting staff user by ID ($STAFF_ID)..."
    curl -s -X GET "${API_URL}/users/${STAFF_ID}" | jq

    # Test getting non-existent user
    echo -e "\n❌ Testing non-existent user (should return 404)..."
    curl -s -X GET "${API_URL}/users/99999" || echo "Expected 404 error"

    # Test duplicate login (should return existing user)
    echo -e "\n🔄 Testing duplicate login (should return existing patient)..."
    curl -s -X POST "${API_URL}/users/login" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "John Doe",
            "email": "john.doe@example.com",
            "age": 30,
            "gender": "male",
            "user_type": "patient"
        }' | jq

    echo -e "\n${GREEN}✅ Users API tests complete!${NC}"
}

# Main command router
case "$1" in
    "install")
        install
        ;;
    "start-ui")
        start_ui
        ;;
    "start-server")
        start_server
        ;;
    "clean")
        clean
        ;;
    "help"|"")
        print_help
        ;;
    "test-api")
        test_api
        ;;
    "test-users")
        test_users_api
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run './cli.sh help' for usage information"
        exit 1
        ;;
esac 