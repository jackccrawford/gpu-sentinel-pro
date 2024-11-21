#!/bin/bash

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "Error: Docker is not running"
        exit 1
    fi
}

# Function to generate a secure random string
generate_secret() {
    openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32
}

# Function to update docker-compose.yml with secure credentials
update_credentials() {
    local pg_password=$(generate_secret)
    local jwt_secret=$(generate_secret)
    local operator_token=$(generate_secret)

    # Create credentials file
    cat > .env.supabase << EOF
POSTGRES_PASSWORD=$pg_password
JWT_SECRET=$jwt_secret
OPERATOR_TOKEN=$operator_token
EOF

    # Update docker-compose.yml with the new credentials
    sed -i.bak "s/your-super-secret-password/$pg_password/g" docker-compose.yml
    sed -i.bak "s/your-super-secret-jwt-token-with-at-least-32-characters/$jwt_secret/g" docker-compose.yml
    sed -i.bak "s/your-super-secret-operator-token/$operator_token/g" docker-compose.yml

    echo "Credentials saved to .env.supabase"
    chmod 600 .env.supabase
}

# Main script
echo "Starting Supabase local setup..."

# Check Docker
check_docker

# Create init directory if it doesn't exist
mkdir -p init

# Generate credentials if they don't exist
if [ ! -f .env.supabase ]; then
    echo "Generating secure credentials..."
    update_credentials
fi

# Start services
echo "Starting Supabase services..."
docker-compose up -d

echo "
Supabase is starting! The following services will be available:
- Studio:  http://localhost:54000
- API:     http://localhost:54001
- Auth:    http://localhost:54002
- REST:    http://localhost:54003
- Meta:    http://localhost:54004
- DB:      localhost:54432

Credentials are stored in .env.supabase
"

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

echo "Setup complete! You can now access Supabase Studio at http://localhost:54000"