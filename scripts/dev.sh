#!/bin/bash

# Personal Finance Manager - Development Helper Script

set -e

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    check_docker
    
    docker compose up -d
    
    print_success "Development environment started!"
    print_status "Access points:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API: http://localhost:8000"
    echo "  - Documentation: http://localhost:8000/docs"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - Mailpit (Email Testing): http://localhost:8025"
}

# Function to stop development environment
stop_dev() {
    print_status "Stopping development environment..."
    docker compose down
    print_success "Development environment stopped!"
}

# Function to restart development environment
restart_dev() {
    print_status "Restarting development environment..."
    stop_dev
    start_dev
}

# Function to view logs
view_logs() {
    print_status "Viewing application logs..."
    docker compose logs -f app
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    docker compose exec app pytest "$@"
}

# Function to format code
format_code() {
    print_status "Formatting code with Black..."
    docker compose exec app black .
    print_success "Code formatted!"
}

# Function to lint code
lint_code() {
    print_status "Linting code with Flake8..."
    docker compose exec app flake8 .
    print_success "Code linting completed!"
}

# Function to check types
check_types() {
    print_status "Checking types with MyPy..."
    docker compose exec app mypy .
    print_success "Type checking completed!"
}

# Function to access database
access_db() {
    print_status "Accessing PostgreSQL database..."
    docker compose exec postgres psql -U pfm_user -d pfm_dev
}

# Function to show status
show_status() {
    print_status "Development environment status:"
    docker compose ps
}

# Function to show help
show_help() {
    echo "Personal Finance Manager - Development Helper Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start development environment"
    echo "  stop        Stop development environment"
    echo "  restart     Restart development environment"
    echo "  logs        View application logs"
    echo "  test        Run tests"
    echo "  format      Format code with Black"
    echo "  lint        Lint code with Flake8"
    echo "  types       Check types with MyPy"
    echo "  db          Access PostgreSQL database"
    echo "  status      Show environment status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 test -v"
    echo "  $0 format"
}

# Main script logic
case "${1:-help}" in
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    logs)
        view_logs
        ;;
    test)
        run_tests "${@:2}"
        ;;
    format)
        format_code
        ;;
    lint)
        lint_code
        ;;
    types)
        check_types
        ;;
    db)
        access_db
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 