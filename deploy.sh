#!/bin/bash
set -e

# ===========================================
# CAAFW Production Deployment Script
# ===========================================

DOMAIN="caafw.org"
EMAIL="admin@caafw.org"  # Change to your email for Let's Encrypt

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check if running as root or with sudo
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root or with sudo"
    fi
}

# Install Docker and Docker Compose if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        log "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        systemctl enable docker
        systemctl start docker
    else
        log "Docker already installed"
    fi

    if ! command -v docker-compose &> /dev/null; then
        log "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    else
        log "Docker Compose already installed"
    fi
}

# Setup environment
setup_env() {
    if [ ! -f .env.production ]; then
        error ".env.production not found! Copy .env.production.example and fill in values."
    fi
    log "Environment file found"
}

# Create necessary directories
create_dirs() {
    log "Creating directories..."
    mkdir -p certbot/www
    mkdir -p certbot/conf
    mkdir -p nginx/ssl
}

# Initial deployment (before SSL)
initial_deploy() {
    log "Starting initial deployment (HTTP only)..."

    # Use initial nginx config (no SSL)
    cp nginx/nginx.initial.conf nginx/nginx.conf.bak
    cp nginx/nginx.initial.conf nginx/nginx.conf

    # Start services
    docker-compose -f docker-compose.prod.yml up -d --build

    log "Waiting for services to start..."
    sleep 30

    # Check if services are running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "Services are running!"
    else
        error "Some services failed to start. Check: docker-compose -f docker-compose.prod.yml logs"
    fi
}

# Obtain SSL certificate
obtain_ssl() {
    log "Obtaining SSL certificate from Let's Encrypt..."

    docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN \
        -d www.$DOMAIN

    if [ $? -eq 0 ]; then
        log "SSL certificate obtained successfully!"
    else
        error "Failed to obtain SSL certificate"
    fi
}

# Switch to SSL nginx config
enable_ssl() {
    log "Enabling SSL configuration..."

    # Restore full SSL nginx config
    cp nginx/nginx.conf.bak nginx/nginx.initial.conf.backup 2>/dev/null || true
    # The main nginx.conf already has SSL config, just need certs

    # Restart nginx to pick up SSL
    docker-compose -f docker-compose.prod.yml restart nginx

    log "SSL enabled!"
}

# Full deployment
deploy() {
    log "Starting full deployment..."
    docker-compose -f docker-compose.prod.yml up -d --build
    log "Deployment complete!"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
    log "Migrations complete!"
}

# Show status
status() {
    log "Service Status:"
    docker-compose -f docker-compose.prod.yml ps
}

# View logs
logs() {
    docker-compose -f docker-compose.prod.yml logs -f "${1:-}"
}

# Stop all services
stop() {
    log "Stopping all services..."
    docker-compose -f docker-compose.prod.yml down
    log "Services stopped"
}

# Backup database
backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    log "Creating database backup: $BACKUP_FILE"
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE
    log "Backup created: $BACKUP_FILE"
}

# Show help
show_help() {
    echo "CAAFW Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Initial setup (install Docker, create dirs)"
    echo "  initial     - First deployment (HTTP only, before SSL)"
    echo "  ssl         - Obtain SSL certificate"
    echo "  ssl-enable  - Switch to SSL configuration"
    echo "  deploy      - Full deployment with SSL"
    echo "  migrate     - Run database migrations"
    echo "  status      - Show service status"
    echo "  logs [svc]  - View logs (optionally for specific service)"
    echo "  stop        - Stop all services"
    echo "  backup      - Backup database"
    echo "  help        - Show this help"
    echo ""
    echo "First-time deployment:"
    echo "  1. ./deploy.sh setup"
    echo "  2. Edit .env.production with your values"
    echo "  3. ./deploy.sh initial"
    echo "  4. ./deploy.sh ssl"
    echo "  5. ./deploy.sh ssl-enable"
    echo "  6. ./deploy.sh migrate"
}

# Main
case "${1:-help}" in
    setup)
        check_root
        install_docker
        create_dirs
        setup_env
        ;;
    initial)
        setup_env
        create_dirs
        initial_deploy
        ;;
    ssl)
        obtain_ssl
        ;;
    ssl-enable)
        enable_ssl
        ;;
    deploy)
        setup_env
        deploy
        ;;
    migrate)
        run_migrations
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    stop)
        stop
        ;;
    backup)
        backup
        ;;
    help|*)
        show_help
        ;;
esac
