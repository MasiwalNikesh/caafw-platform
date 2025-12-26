# Deploying CAAFW to Production on AWS EC2

## Prerequisites

- AWS Account
- Domain `caafw.org` with DNS access
- SSH key pair for EC2

## Step 1: Launch EC2 Instance

### Recommended Instance
- **Type**: t3.medium (2 vCPU, 4GB RAM) - ~$30/month
- **AMI**: Ubuntu 22.04 LTS
- **Storage**: 50GB gp3 SSD
- **Security Group**:
  - SSH (22) - Your IP only
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere

### Launch Commands
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## Step 2: Configure DNS

Point your domain to the EC2 instance:

| Record | Type | Value |
|--------|------|-------|
| @ | A | [EC2 Public IP] |
| www | A | [EC2 Public IP] |

Wait for DNS propagation (5-30 minutes).

## Step 3: Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-repo/ai-community-platform.git
cd ai-community-platform

# Create production environment file
cp .env.production.example .env.production

# Edit with your production values
nano .env.production
```

### Required .env.production Values

```bash
# Generate secure secrets
openssl rand -hex 32  # For SECRET_KEY
openssl rand -base64 24  # For POSTGRES_PASSWORD
openssl rand -base64 24  # For REDIS_PASSWORD
```

Fill in these critical values:
- `SECRET_KEY` - 64-character random string
- `POSTGRES_PASSWORD` - Strong database password
- `REDIS_PASSWORD` - Strong Redis password
- API keys for external services

## Step 4: Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Initial setup (installs Docker, creates directories)
sudo ./deploy.sh setup

# Start services (HTTP only, needed for SSL verification)
sudo ./deploy.sh initial

# Obtain SSL certificate from Let's Encrypt
sudo ./deploy.sh ssl

# Enable HTTPS
sudo ./deploy.sh ssl-enable

# Run database migrations
sudo ./deploy.sh migrate
```

## Step 5: Verify Deployment

```bash
# Check service status
sudo ./deploy.sh status

# View logs
sudo ./deploy.sh logs

# Test endpoints
curl https://caafw.org/health
curl https://caafw.org/api/v1/products
```

## Maintenance Commands

```bash
# Update deployment
git pull
sudo ./deploy.sh deploy

# View logs for specific service
sudo ./deploy.sh logs backend
sudo ./deploy.sh logs frontend
sudo ./deploy.sh logs nginx

# Backup database
sudo ./deploy.sh backup

# Stop all services
sudo ./deploy.sh stop
```

## SSL Certificate Renewal

SSL certificates are automatically renewed by the certbot container. To manually renew:

```bash
docker-compose -f docker-compose.prod.yml run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

## Monitoring

### Health Checks
- Frontend: `https://caafw.org/`
- Backend: `https://caafw.org/health`
- API Docs: `https://caafw.org/docs`

### Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Troubleshooting

### Services not starting
```bash
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml ps
```

### Database connection issues
```bash
docker-compose -f docker-compose.prod.yml exec postgres psql -U caafw_prod -d ai_community_prod
```

### SSL issues
```bash
# Check certificate
openssl s_client -connect caafw.org:443 -servername caafw.org

# Re-obtain certificate
sudo ./deploy.sh ssl
sudo ./deploy.sh ssl-enable
```

## Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| EC2 t3.medium | ~$30 |
| EBS 50GB gp3 | ~$4 |
| Data transfer | ~$5-10 |
| **Total** | **~$40-45/month** |

## Security Checklist

- [ ] SSH key-only authentication
- [ ] Security group limits SSH to your IP
- [ ] Strong passwords in .env.production
- [ ] API keys secured
- [ ] Regular backups enabled
- [ ] Monitoring/alerting setup (optional)
