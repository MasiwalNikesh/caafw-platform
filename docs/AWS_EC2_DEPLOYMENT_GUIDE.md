# CAAFW Platform - AWS EC2 Deployment Guide

Complete step-by-step guide to deploy the AI Community Platform on AWS EC2.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Create EC2 Instance](#create-ec2-instance)
4. [Configure Security Group](#configure-security-group)
5. [Allocate Elastic IP](#allocate-elastic-ip)
6. [Configure DNS](#configure-dns)
7. [Connect to EC2](#connect-to-ec2)
8. [Server Setup](#server-setup)
9. [Deploy Application](#deploy-application)
10. [SSL Certificate Setup](#ssl-certificate-setup)
11. [Verify Deployment](#verify-deployment)
12. [Post-Deployment](#post-deployment)
13. [Monitoring & Maintenance](#monitoring--maintenance)
14. [Troubleshooting](#troubleshooting)
15. [Cost Optimization](#cost-optimization)

---

## Prerequisites

Before starting, ensure you have:

- [ ] AWS Account with billing enabled
- [ ] Domain name `caafw.org` with DNS access
- [ ] SSH client installed (Terminal on Mac/Linux, PuTTY on Windows)
- [ ] Git installed locally
- [ ] API keys ready (GitHub, YouTube, Product Hunt, etc.)

---

## AWS Account Setup

### 1. Create AWS Account (if needed)

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Complete registration with payment method
4. Verify email and phone number

### 2. Set Up IAM User (Recommended)

1. Go to **IAM** in AWS Console
2. Click **Users** → **Add users**
3. Create user with:
   - Username: `caafw-admin`
   - Access type: AWS Management Console access
4. Attach policy: `AdministratorAccess`
5. Save credentials securely

### 3. Set Up Billing Alerts

1. Go to **Billing** → **Budgets**
2. Create budget:
   - Monthly budget: $50
   - Alert at 80% threshold
   - Email notification

---

## Create EC2 Instance

### Step 1: Launch Instance

1. Go to **EC2** in AWS Console
2. Select region: `us-east-1` (N. Virginia) or nearest to your users
3. Click **Launch Instance**

### Step 2: Configure Instance

| Setting | Value |
|---------|-------|
| **Name** | `caafw-production` |
| **AMI** | Ubuntu Server 22.04 LTS (HVM), SSD Volume Type |
| **Architecture** | 64-bit (x86) |
| **Instance Type** | t3.medium (2 vCPU, 4 GB RAM) |

### Step 3: Key Pair

1. Click **Create new key pair**
2. Settings:
   - Name: `caafw-key`
   - Type: RSA
   - Format: `.pem` (Mac/Linux) or `.ppk` (Windows/PuTTY)
3. Download and save securely
4. On Mac/Linux, set permissions:
   ```bash
   chmod 400 ~/Downloads/caafw-key.pem
   mv ~/Downloads/caafw-key.pem ~/.ssh/
   ```

### Step 4: Network Settings

1. Click **Edit** in Network settings
2. Configure:
   - VPC: Default VPC
   - Subnet: No preference
   - Auto-assign public IP: **Enable**

### Step 5: Storage

1. Configure root volume:
   - Size: **50 GB**
   - Volume type: **gp3**
   - IOPS: 3000 (default)
   - Throughput: 125 MB/s (default)
   - Delete on termination: Yes

### Step 6: Launch

1. Review summary
2. Click **Launch instance**
3. Wait for instance to reach "Running" state

---

## Configure Security Group

### Create Security Group

1. Go to **EC2** → **Security Groups**
2. Find the security group attached to your instance
3. Click **Edit inbound rules**

### Inbound Rules

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH Access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web Traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure Web Traffic |

### Outbound Rules

| Type | Protocol | Port | Destination | Description |
|------|----------|------|-------------|-------------|
| All traffic | All | All | 0.0.0.0/0 | Allow all outbound |

---

## Allocate Elastic IP

Elastic IP ensures your server keeps the same IP after restarts.

1. Go to **EC2** → **Elastic IPs**
2. Click **Allocate Elastic IP address**
3. Click **Allocate**
4. Select the new Elastic IP
5. Click **Actions** → **Associate Elastic IP address**
6. Select your instance: `caafw-production`
7. Click **Associate**

**Save this IP address** - you'll need it for DNS configuration.

---

## Configure DNS

### Option A: Using AWS Route 53

1. Go to **Route 53** → **Hosted zones**
2. Create hosted zone for `caafw.org`
3. Add records:

| Record Name | Type | Value | TTL |
|-------------|------|-------|-----|
| caafw.org | A | [Elastic IP] | 300 |
| www.caafw.org | A | [Elastic IP] | 300 |

4. Update nameservers at your domain registrar

### Option B: Using External DNS (GoDaddy, Namecheap, etc.)

1. Log in to your domain registrar
2. Go to DNS Management
3. Add/Edit A records:

| Host | Type | Points to | TTL |
|------|------|-----------|-----|
| @ | A | [Elastic IP] | 600 |
| www | A | [Elastic IP] | 600 |

### Verify DNS Propagation

```bash
# Check DNS resolution (may take 5-30 minutes)
dig caafw.org +short
dig www.caafw.org +short

# Or use online tool
# https://dnschecker.org
```

---

## Connect to EC2

### From Mac/Linux

```bash
# Connect via SSH
ssh -i ~/.ssh/caafw-key.pem ubuntu@[ELASTIC-IP]

# Example
ssh -i ~/.ssh/caafw-key.pem ubuntu@54.123.45.67
```

### From Windows (PuTTY)

1. Open PuTTY
2. Host Name: `ubuntu@[ELASTIC-IP]`
3. Port: 22
4. Connection → SSH → Auth → Credentials
5. Browse to your `.ppk` file
6. Click **Open**

### First Connection

You'll see a fingerprint warning - type `yes` to continue.

---

## Server Setup

Run these commands after connecting to EC2:

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    htop \
    nano
```

### 3. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Apply group changes (or logout/login)
newgrp docker

# Verify installation
docker --version
docker compose version
```

### 4. Configure Swap (Recommended for t3.medium)

```bash
# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify
free -h
```

### 5. Configure Firewall (UFW)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verify
sudo ufw status
```

---

## Deploy Application

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/MasiwalNikesh/caafw-platform.git
cd caafw-platform
```

### 2. Create Production Environment File

```bash
cp .env.production.example .env.production
nano .env.production
```

### 3. Generate Secure Secrets

```bash
# Generate SECRET_KEY (64 characters)
openssl rand -hex 32

# Generate POSTGRES_PASSWORD
openssl rand -base64 24

# Generate REDIS_PASSWORD
openssl rand -base64 24
```

### 4. Edit .env.production

Fill in all required values:

```bash
# Core Settings
DEBUG=false
ENVIRONMENT=production
SECRET_KEY=<paste-generated-secret>

# Database
POSTGRES_USER=caafw_prod
POSTGRES_PASSWORD=<paste-generated-password>
POSTGRES_DB=ai_community_prod

# Redis
REDIS_PASSWORD=<paste-generated-password>

# Domain
DOMAIN=caafw.org
NEXT_PUBLIC_API_URL=https://caafw.org

# OAuth Redirect URIs
GOOGLE_REDIRECT_URI=https://caafw.org/auth/callback/google
MICROSOFT_REDIRECT_URI=https://caafw.org/auth/callback/microsoft
LINKEDIN_REDIRECT_URI=https://caafw.org/auth/callback/linkedin

# API Keys (fill in your keys)
GITHUB_TOKEN=
YOUTUBE_API_KEY=
PRODUCT_HUNT_TOKEN=
# ... etc
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### 5. Update Deploy Script Email

```bash
nano deploy.sh
# Change EMAIL="admin@caafw.org" to your email
```

### 6. Create Required Directories

```bash
mkdir -p certbot/www certbot/conf nginx/ssl
```

### 7. Initial Deployment (HTTP Only)

```bash
# Use initial nginx config (no SSL yet)
cp nginx/nginx.initial.conf nginx/nginx.conf

# Build and start services
docker compose -f docker-compose.prod.yml up -d --build

# Watch the build process
docker compose -f docker-compose.prod.yml logs -f
# Press Ctrl+C to exit logs
```

### 8. Verify Services Running

```bash
docker compose -f docker-compose.prod.yml ps
```

All services should show "Up" status.

---

## SSL Certificate Setup

### 1. Verify DNS is Working

```bash
# From your local machine, verify domain resolves
curl -I http://caafw.org
```

You should get a response (even if it's an error page).

### 2. Obtain SSL Certificate

```bash
# Request certificate from Let's Encrypt
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email admin@caafw.org \
    --agree-tos \
    --no-eff-email \
    -d caafw.org \
    -d www.caafw.org
```

### 3. Switch to SSL Configuration

```bash
# Replace nginx config with SSL version
cp nginx/nginx.conf nginx/nginx.http.backup
cat > nginx/nginx.conf << 'NGINX_CONF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent"';
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript
               application/xml application/xml+rss text/javascript;

    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name caafw.org www.caafw.org;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name caafw.org www.caafw.org;

        ssl_certificate /etc/letsencrypt/live/caafw.org/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/caafw.org/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=63072000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;

        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /redoc {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }

        location /openapi.json {
            proxy_pass http://backend;
        }

        location /health {
            proxy_pass http://backend;
        }

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /_next/static/ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
NGINX_CONF
```

### 4. Restart Nginx

```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### 5. Run Database Migrations

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Verify Deployment

### Test Endpoints

```bash
# Health check
curl https://caafw.org/health

# API endpoint
curl https://caafw.org/api/v1/products

# Check SSL certificate
openssl s_client -connect caafw.org:443 -servername caafw.org < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

### Access URLs

| URL | Purpose |
|-----|---------|
| https://caafw.org | Main website |
| https://caafw.org/docs | API Documentation (Swagger) |
| https://caafw.org/redoc | API Documentation (ReDoc) |
| https://caafw.org/health | Health check endpoint |
| https://caafw.org/admin | Admin dashboard |

---

## Post-Deployment

### 1. Create Admin User

```bash
docker compose -f docker-compose.prod.yml exec backend python scripts/seed_admin.py
```

### 2. Seed Initial Data (Optional)

```bash
docker compose -f docker-compose.prod.yml exec backend python scripts/seed_learning_paths.py
```

### 3. Set Up Automatic SSL Renewal

The certbot container automatically renews certificates. Verify it's running:

```bash
docker compose -f docker-compose.prod.yml ps certbot
```

### 4. Configure Backups

Create a backup script:

```bash
cat > ~/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

cd ~/caafw-platform
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U caafw_prod ai_community_prod > $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql"
EOF

chmod +x ~/backup.sh
```

Add to crontab for daily backups:

```bash
crontab -e
# Add this line:
0 3 * * * /home/ubuntu/backup.sh >> /home/ubuntu/backup.log 2>&1
```

---

## Monitoring & Maintenance

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f postgres
```

### Check Service Status

```bash
docker compose -f docker-compose.prod.yml ps
```

### Resource Usage

```bash
# Container stats
docker stats

# System resources
htop
df -h
free -h
```

### Update Application

```bash
cd ~/caafw-platform
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend
```

---

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check specific service
docker compose -f docker-compose.prod.yml logs backend

# Rebuild containers
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Database Connection Issues

```bash
# Connect to database
docker compose -f docker-compose.prod.yml exec postgres psql -U caafw_prod -d ai_community_prod

# Check database logs
docker compose -f docker-compose.prod.yml logs postgres
```

### SSL Certificate Issues

```bash
# Check certificate status
docker compose -f docker-compose.prod.yml run --rm certbot certificates

# Force renewal
docker compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart nginx
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes

# Remove old logs
sudo journalctl --vacuum-time=3d
```

### Out of Memory

```bash
# Check memory
free -h

# Check swap
swapon --show

# Identify memory hogs
docker stats --no-stream
```

---

## Cost Optimization

### Current Setup Cost (~$40-45/month)

| Resource | Cost |
|----------|------|
| EC2 t3.medium (on-demand) | ~$30/month |
| EBS 50GB gp3 | ~$4/month |
| Elastic IP | Free (when attached) |
| Data Transfer | ~$5-10/month |

### Save Money with Reserved Instances

1. Go to **EC2** → **Reserved Instances**
2. Purchase 1-year reservation for t3.medium
3. Save up to 40% (~$18/month instead of $30)

### Save Money with Spot Instances (Not recommended for production)

Only use for development/staging environments.

### Scale Down When Needed

```bash
# Stop instance when not needed (dev/staging)
aws ec2 stop-instances --instance-ids i-xxxxx

# Start when needed
aws ec2 start-instances --instance-ids i-xxxxx
```

---

## Security Best Practices

### Completed

- [x] SSH key-only authentication
- [x] Security group restricts SSH to your IP
- [x] HTTPS enabled with auto-renewal
- [x] Non-root Docker user
- [x] Strong passwords generated
- [x] UFW firewall enabled

### Recommended Additional Steps

1. **Enable AWS CloudWatch monitoring**
2. **Set up AWS SNS alerts for high CPU/memory**
3. **Enable AWS backup for EBS volumes**
4. **Use AWS Secrets Manager for API keys** (advanced)
5. **Set up fail2ban for SSH protection**:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

---

## Quick Reference

### SSH Connect
```bash
ssh -i ~/.ssh/caafw-key.pem ubuntu@[ELASTIC-IP]
```

### Deploy Commands
```bash
cd ~/caafw-platform
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml ps
```

### Useful Aliases

Add to `~/.bashrc`:

```bash
alias dc="docker compose -f docker-compose.prod.yml"
alias dclogs="docker compose -f docker-compose.prod.yml logs -f"
alias dcps="docker compose -f docker-compose.prod.yml ps"
alias dcrestart="docker compose -f docker-compose.prod.yml restart"
```

Then run: `source ~/.bashrc`

---

## Support

- **Repository**: https://github.com/MasiwalNikesh/caafw-platform
- **AWS Documentation**: https://docs.aws.amazon.com/ec2/
- **Docker Documentation**: https://docs.docker.com/

---

*Last updated: December 2024*
