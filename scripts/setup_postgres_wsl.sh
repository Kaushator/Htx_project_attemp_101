#!/bin/bash
# Local PostgreSQL Setup for WSL (без Docker)

echo "🐘 Setting up local PostgreSQL in WSL..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
sudo service postgresql start

# Setup database manually
echo "Creating database and user..."
echo "You may need to enter your sudo password..."

# Create database and user with manual commands
sudo -u postgres createdb htx_project 2>/dev/null || echo "Database htx_project already exists"

# Create user and set permissions
sudo -u postgres psql -c "CREATE USER htx_user WITH PASSWORD 'htx_pass123';" 2>/dev/null || echo "User htx_user already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE htx_project TO htx_user;"
sudo -u postgres psql -c "ALTER USER htx_user CREATEDB;"

# Connect to database and grant schema permissions
sudo -u postgres psql htx_project -c "GRANT ALL ON SCHEMA public TO htx_user;"
sudo -u postgres psql htx_project -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO htx_user;"
sudo -u postgres psql htx_project -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO htx_user;"

echo "✅ PostgreSQL setup completed!"
echo ""
echo "📋 Connection Details:"
echo "Host: localhost"
echo "Port: 5432"
echo "Database: htx_project"
echo "User: htx_user"
echo "Password: htx_pass123"
echo ""
echo "🔗 Connection URL:"
echo "postgresql://htx_user:htx_pass123@localhost:5432/htx_project"
echo ""
echo "🔧 Testing connection..."
PGPASSWORD=htx_pass123 psql -h localhost -U htx_user -d htx_project -c "SELECT version();" || echo "❌ Connection test failed"
