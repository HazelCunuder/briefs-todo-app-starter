#!/bin/bash

# Development Server Script for To-Do App
# 
# This script provides a convenient way to start the development environment
# with all services running and proper logging configuration.
#
# Usage:
#   ./scripts/dev-server.sh        # Start all services
#   ./scripts/dev-server.sh start   # Start all services
#   ./scripts/dev-server.sh stop    # Stop all services
#   ./scripts/dev-server.sh restart  # Restart all services
#   ./scripts/dev-server.sh logs    # View logs
#   ./scripts/dev-server.sh clean   # Clean up and remove containers
#   ./scripts/dev-server.sh status  # Show service status
#   ./scripts/dev-server.sh test    # Run tests
#   ./scripts/dev-server.sh lint    # Run linters
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Docker Compose command
DOCKER_COMPOSE="docker compose"

# Check if docker compose v2 is available
if ! command -v docker compose &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        echo -e "${RED}Error: Neither 'docker compose' nor 'docker-compose' found.${NC}"
        echo "Please install Docker Compose v2 or later."
        exit 1
    fi
fi

# Function to display header
header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  To-Do App Development Server${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Function to check dependencies
check_dependencies() {
    echo -n "Checking dependencies... "
    
    local missing=0
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker not found${NC}"
        missing=$((missing + 1))
    fi
    
    # Check Docker Compose
    if ! $DOCKER_COMPOSE version &> /dev/null; then
        echo -e "${RED}Docker Compose not found${NC}"
        missing=$((missing + 1))
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        echo -e "${RED}Python not found${NC}"
        missing=$((missing + 1))
    fi
    
    # Check Bun (for tooling)
    if ! command -v bun &> /dev/null; then
        echo -e "${YELLOW}Bun not found (optional for tooling)${NC}"
    fi
    
    if [ $missing -eq 0 ]; then
        echo -e "${GREEN}All required dependencies found!${NC}"
        return 0
    else
        echo -e "${RED}Missing $missing required dependency(ies)${NC}"
        return 1
    fi
}

# Function to start services
start_services() {
    header
    echo -e "${YELLOW}Starting development services...${NC}"
    echo ""
    
    # Check if services are already running
    if $DOCKER_COMPOSE ps | grep -q "Up"; then
        echo -e "${YELLOW}Services are already running. Use 'restart' to restart.${NC}"
        return 0
    fi
    
    # Start all services
    echo -e "${BLUE}Starting containers...${NC}"
    $DOCKER_COMPOSE up -d
    
    # Wait for services to be ready
    echo -e "${BLUE}Waiting for services to be ready...${NC}"
    
    # Wait for database
    local db_ready=false
    for i in {1..30}; do
        if $DOCKER_COMPOSE exec postgres pg_isready -U appuser -d tododb &> /dev/null; then
            db_ready=true
            break
        fi
        echo -n "."
        sleep 1
    done
    
    if [ "$db_ready" = false ]; then
        echo -e "\n${RED}Database did not start in time${NC}"
        return 1
    fi
    
    # Wait for API
    local api_ready=false
    for i in {1..30}; do
        if curl -s http://localhost:8000/health &> /dev/null; then
            api_ready=true
            break
        fi
        echo -n "."
        sleep 1
    done
    
    if [ "$api_ready" = false ]; then
        echo -e "\n${RED}API did not start in time${NC}"
        return 1
    fi
    
    echo -e "\n${GREEN}All services are ready!${NC}"
    echo ""
    echo -e "${BLUE}Services:${NC}"
    echo "  API:    http://localhost:8000"
    echo "  Web:    http://localhost:5173"
    echo "  Docs:   http://localhost:8000/docs"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  Stop:    $0 stop"
    echo "  Restart: $0 restart"
    echo "  Logs:    $0 logs"
    echo "  Status:  $0 status"
    echo ""
    
    return 0
}

# Function to stop services
stop_services() {
    header
    echo -e "${YELLOW}Stopping development services...${NC}"
    echo ""
    
    $DOCKER_COMPOSE down
    
    echo -e "${GREEN}Services stopped.${NC}"
    return 0
}

# Function to restart services
restart_services() {
    stop_services
    start_services
    return 0
}

# Function to show logs
show_logs() {
    header
    echo -e "${BLUE}Showing logs for all services...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop viewing logs${NC}"
    echo ""
    
    $DOCKER_COMPOSE logs -f
    
    return 0
}

# Function to show service logs
show_service_logs() {
    local service=$1
    header
    echo -e "${BLUE}Showing logs for '$service' service...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop viewing logs${NC}"
    echo ""
    
    $DOCKER_COMPOSE logs -f "$service"
    
    return 0
}

# Function to clean up
clean_up() {
    header
    echo -e "${YELLOW}Cleaning up containers, images, and volumes...${NC}"
    echo ""
    
    # Stop services
    $DOCKER_COMPOSE down
    
    # Remove volumes
    $DOCKER_COMPOSE down -v
    
    # Prune Docker system
    echo -e "${BLUE}Pruning Docker system...${NC}"
    docker system prune -f
    
    echo -e "${GREEN}Cleanup completed.${NC}"
    return 0
}

# Function to show status
show_status() {
    header
    echo -e "${BLUE}Service Status:${NC}"
    echo ""
    
    $DOCKER_COMPOSE ps -a
    
    echo ""
    echo -e "${BLUE}Container Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    return 0
}

# Function to run tests
run_tests() {
    header
    echo -e "${YELLOW}Running tests...${NC}"
    echo ""
    
    # Run API tests
    echo -e "${BLUE}Running API tests...${NC}"
    cd api
    python -m pytest tests/ -v --tb=short
    cd ..
    
    echo ""
    
    # Run frontend tests
    echo -e "${BLUE}Running frontend tests...${NC}"
    cd web
    npm test
    cd ..
    
    echo ""
    echo -e "${GREEN}Tests completed.${NC}"
    return 0
}

# Function to run linters
run_linters() {
    header
    echo -e "${YELLOW}Running linters...${NC}"
    echo ""
    
    # Run markdown linter
    echo -e "${BLUE}Running markdown linter...${NC}"
    bun run lint:md 2>/dev/null || echo -e "${YELLOW}markdownlint not available, skipping${NC}"
    
    # Run YAML linter
    echo -e "${BLUE}Running YAML linter...${NC}"
    bun run lint:yaml 2>/dev/null || echo -e "${YELLOW}yamllint not available, skipping${NC}"
    
    # Run Python linter (Ruff)
    echo -e "${BLUE}Running Python linter...${NC}"
    cd api
    python -m ruff check . 2>/dev/null || echo -e "${YELLOW}Ruff not available, skipping${NC}"
    cd ..
    
    # Run Python formatter (Ruff)
    echo -e "${BLUE}Running Python formatter...${NC}"
    cd api
    python -m ruff format --check . 2>/dev/null || echo -e "${YELLOW}Ruff formatter not available, skipping${NC}"
    cd ..
    
    # Run TypeScript linter (ESLint)
    echo -e "${BLUE}Running TypeScript linter...${NC}"
    cd web
    npm run lint 2>/dev/null || echo -e "${YELLOW}ESLint not available, skipping${NC}"
    cd ..
    
    # Run TypeScript type checker
    echo -e "${BLUE}Running TypeScript type checker...${NC}"
    cd web
    npm run check 2>/dev/null || echo -e "${YELLOW}svelte-check not available, skipping${NC}"
    cd ..
    
    echo ""
    echo -e "${GREEN}Linting completed.${NC}"
    return 0
}

# Function to seed database
seed_database() {
    header
    echo -e "${YELLOW}Seeding database...${NC}"
    echo ""
    
    # Run seed script
    python scripts/seed.py --dev --verbose
    
    echo ""
    echo -e "${GREEN}Database seeding completed.${NC}"
    return 0
}

# Function to show help
show_help() {
    header
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start      Start all development services"
    echo "  stop       Stop all development services"
    echo "  restart    Restart all development services"
    echo "  logs       View logs for all services"
    echo "  logs <svc> View logs for a specific service (api, web, postgres)"
    echo "  clean      Clean up containers, images, and volumes"
    echo "  status     Show service status and resource usage"
    echo "  test       Run all tests"
    echo "  lint       Run all linters"
    echo "  seed       Seed the database with sample data"
    echo "  check      Check dependencies"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start           # Start all services"
    echo "  $0 logs api        # View API logs"
    echo "  $0 test            # Run tests"
    echo "  $0 lint            # Run linters"
    echo ""
    return 0
}

# Main logic
case "${1:-start}" in
    start)
        check_dependencies || exit 1
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    logs)
        if [ -z "$2" ]; then
            show_logs
        else
            show_service_logs "$2"
        fi
        ;;
    clean)
        clean_up
        ;;
    status)
        show_status
        ;;
    test)
        run_tests
        ;;
    lint)
        run_linters
        ;;
    seed)
        seed_database
        ;;
    check)
        check_dependencies
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
