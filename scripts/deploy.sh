#!/bin/bash

# Personal Finance Manager - Deployment Script
# This script handles code deployment and database migrations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if containers are running
check_containers() {
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Containers are not running. Please start them first with: docker-compose up -d"
        exit 1
    fi
}

# Function to wait for database to be ready
wait_for_database() {
    print_status "Waiting for database to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U pfm_user -d pfm_dev > /dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Database not ready yet, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Database failed to start within $max_attempts attempts"
    exit 1
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Check if alembic is available
    if ! docker-compose exec -T app alembic --help > /dev/null 2>&1; then
        print_error "Alembic is not available. Please ensure it's installed."
        exit 1
    fi
    
    # Get current migration version
    local current_version=$(docker-compose exec -T app alembic current 2>/dev/null | grep -o '[0-9a-f]*' || echo "None")
    print_status "Current migration version: $current_version"
    
    # Run migrations
    if docker-compose exec -T app alembic upgrade head; then
        print_success "Database migrations completed successfully"
    else
        print_error "Database migrations failed"
        exit 1
    fi
}

# Function to restart application
restart_app() {
    print_status "Restarting application..."
    
    # Restart only the app container to preserve database data
    if docker-compose restart app; then
        print_success "Application restarted successfully"
    else
        print_error "Failed to restart application"
        exit 1
    fi
}

# Function to check application health
check_app_health() {
    print_status "Checking application health..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Application is healthy"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Application not ready yet, waiting..."
        sleep 3
        attempt=$((attempt + 1))
    done
    
    print_error "Application failed to start within $max_attempts attempts"
    exit 1
}

# Function to show deployment summary
show_summary() {
    print_success "Deployment completed successfully!"
    echo
    echo "Application URLs:"
    echo "  - API: http://localhost:8000"
    echo "  - Documentation: http://localhost:8000/docs"
    echo "  - Frontend: http://localhost:3000"
    echo
    echo "To view logs:"
    echo "  - Application: docker-compose logs -f app"
    echo "  - Database: docker-compose logs -f postgres"
    echo
    echo "To run tests:"
    echo "  docker-compose exec app pytest"
}

# Main deployment function
deploy() {
    print_status "Starting deployment process..."
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check if containers are running
    check_containers
    
    # Wait for database to be ready
    wait_for_database
    
    # Run database migrations
    run_migrations
    
    # Restart application
    restart_app
    
    # Check application health
    check_app_health
    
    # Show summary
    show_summary
}

# Function to show help
show_help() {
    echo "Personal Finance Manager - Deployment Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  deploy     - Full deployment with migrations (default)"
    echo "  migrate    - Run database migrations only"
    echo "  restart    - Restart application only"
    echo "  health     - Check application health"
    echo "  help       - Show this help message"
    echo
    echo "Examples:"
    echo "  $0 deploy     # Full deployment"
    echo "  $0 migrate    # Run migrations only"
    echo "  $0 restart    # Restart app only"
}

# Main script logic
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "migrate")
        check_containers
        wait_for_database
        run_migrations
        ;;
    "restart")
        check_containers
        restart_app
        check_app_health
        ;;
    "health")
        check_app_health
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 