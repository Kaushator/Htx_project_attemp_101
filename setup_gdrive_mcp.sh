#!/bin/bash
# Google Drive MCP Server Setup Script

set -e

echo "🚀 Google Drive MCP Server Setup"
echo "================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if Node.js is installed
check_nodejs() {
    print_header "Checking Node.js Installation"
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_status "Node.js is installed: $NODE_VERSION"
        
        # Check version is >= 18
        NODE_MAJOR=$(echo $NODE_VERSION | sed 's/v//' | cut -d. -f1)
        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_error "Node.js version 18+ required, found: $NODE_VERSION"
            echo "Please upgrade Node.js: https://nodejs.org/"
            exit 1
        fi
    else
        print_error "Node.js not found"
        echo "Please install Node.js 18+: https://nodejs.org/"
        exit 1
    fi
    
    if command -v npx &> /dev/null; then
        print_status "npx is available"
    else
        print_error "npx not found"
        exit 1
    fi
}

# Create credentials directory
setup_credentials_dir() {
    print_header "Setting up Credentials Directory"
    
    CREDS_DIR="$HOME/.config/gdrive-mcp"
    mkdir -p "$CREDS_DIR"
    print_status "Created credentials directory: $CREDS_DIR"
    
    echo "CREDS_DIR=$CREDS_DIR"
}

# Instructions for OAuth setup
show_oauth_instructions() {
    print_header "Google OAuth Setup Instructions"
    
    cat << 'EOF'

📋 To set up Google Drive MCP server, you need to:

1. 🌐 Go to Google Cloud Console: https://console.cloud.google.com/

2. 📁 Create or select a project:
   - Click "Select a project" dropdown
   - Click "New Project" if needed
   - Give it a name like "MCP-GDrive-Integration"

3. 🔌 Enable Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and click "Enable"

4. 🔑 Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - If prompted, configure OAuth consent screen:
     - Choose "External" user type
     - Fill in App name: "MCP GDrive"
     - Add your email as developer contact
     - Save and continue through scopes (no changes needed)
     - Add your email as test user
   - Choose "Desktop application" as application type
   - Name it "MCP GDrive Client"
   - Click "Create"
   - Download the JSON file

5. 💾 Save the credentials:
   - Rename the downloaded file to "credentials.json"
   - Place it in: ~/.config/gdrive-mcp/

EOF

    echo -e "${YELLOW}After completing these steps, press Enter to continue...${NC}"
    read -r
}

# Check for credentials file
check_credentials() {
    print_header "Checking Credentials"
    
    CREDS_FILE="$HOME/.config/gdrive-mcp/credentials.json"
    
    if [ -f "$CREDS_FILE" ]; then
        print_status "Credentials file found: $CREDS_FILE"
        return 0
    else
        print_error "Credentials file not found: $CREDS_FILE"
        print_warning "Please follow the OAuth setup instructions above"
        return 1
    fi
}

# Test MCP server
test_mcp_server() {
    print_header "Testing MCP Server"
    
    print_status "Installing/updating Google Drive MCP server..."
    npx -y @modelcontextprotocol/server-gdrive@latest --version
    
    print_status "Testing authentication..."
    CREDS_FILE="$HOME/.config/gdrive-mcp/credentials.json"
    
    if [ -f "$CREDS_FILE" ]; then
        print_status "Running authentication flow..."
        # The server will handle OAuth flow automatically
        npx -y @modelcontextprotocol/server-gdrive auth --credentials "$CREDS_FILE"
    else
        print_error "Credentials file missing. Please complete OAuth setup first."
        return 1
    fi
}

# Create MCP configuration
create_mcp_config() {
    print_header "Creating MCP Configuration"
    
    cat << 'EOF'

📝 MCP Server Configuration for Qoder:

Add this configuration to your Qoder MCP settings:

Server Name: gdrive
Command: npx
Arguments: ["@modelcontextprotocol/server-gdrive"]

The server will automatically find credentials in ~/.config/gdrive-mcp/

EOF
}

# Main execution
main() {
    echo "Starting Google Drive MCP Server setup..."
    
    check_nodejs
    setup_credentials_dir
    show_oauth_instructions
    
    if check_credentials; then
        test_mcp_server
        create_mcp_config
        print_status "✅ Setup completed successfully!"
        echo ""
        print_status "Next steps:"
        echo "1. Add the MCP server configuration in Qoder"
        echo "2. Restart Qoder IDE"
        echo "3. Test the Google Drive integration"
    else
        print_error "Setup incomplete. Please complete the OAuth setup first."
        exit 1
    fi
}

# Run main function
main "$@"