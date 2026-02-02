# Deployment Guide

This guide covers deploying the QR Code Generator application to production.

## Option 1: Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Step 1: Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

CMD ["node", "server.js"]
```

### Step 3: Create docker-compose.yml

Create `docker-compose.yml` in root:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: qrcode_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/qrcode_db
      CORS_ORIGINS: http://localhost:3000,https://yourdomain.com
    depends_on:
      - db
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### Step 4: Deploy
```bash
docker-compose up -d
```

## Option 2: Vercel (Frontend) + Railway (Backend + DB)

### Backend & Database on Railway

1. Sign up at https://railway.app
2. Create a new project
3. Add PostgreSQL database
4. Deploy backend:
   - Connect your GitHub repository
   - Select the `backend` directory
   - Add environment variables:
     - `DATABASE_URL` (automatically provided by Railway)
     - `CORS_ORIGINS` (your frontend URL)
   - Deploy

### Frontend on Vercel

1. Sign up at https://vercel.com
2. Import your GitHub repository
3. Configure:
   - Framework: Next.js
   - Root Directory: `frontend`
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL` (Your Railway backend URL)
4. Deploy

## Option 3: AWS Deployment

### Backend on AWS Elastic Beanstalk
1. Install AWS CLI and EB CLI
2. Initialize Elastic Beanstalk:
```bash
cd backend
eb init -p python-3.11 qrcode-backend
```
3. Create environment:
```bash
eb create qrcode-backend-env
```
4. Set environment variables:
```bash
eb setenv DATABASE_URL="postgresql://..." CORS_ORIGINS="https://..."
```
5. Deploy:
```bash
eb deploy
```

### Frontend on AWS Amplify
1. Connect GitHub repository
2. Select `frontend` directory
3. Add environment variables
4. Deploy

### Database on AWS RDS
1. Create PostgreSQL instance
2. Update DATABASE_URL in backend

## Option 4: Traditional VPS (DigitalOcean, Linode, etc.)

### Prerequisites
- Ubuntu 22.04 LTS server
- Domain name (optional)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install nginx -y
```

### Step 2: Database Setup
```bash
sudo -u postgres psql
CREATE DATABASE qrcode_db;
CREATE USER qrcode_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE qrcode_db TO qrcode_user;
\q
```

### Step 3: Deploy Backend
```bash
# Clone repository
git clone https://github.com/yourusername/QRcodegen.git
cd QRcodegen/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://qrcode_user:your_password@localhost/qrcode_db
CORS_ORIGINS=https://yourdomain.com
EOF

# Install and configure systemd service
sudo nano /etc/systemd/system/qrcode-backend.service
```

Create service file:
```ini
[Unit]
Description=QR Code Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/QRcodegen/backend
Environment="PATH=/home/ubuntu/QRcodegen/backend/venv/bin"
ExecStart=/home/ubuntu/QRcodegen/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start qrcode-backend
sudo systemctl enable qrcode-backend
```

### Step 4: Deploy Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Build
npm run build

# Install PM2
sudo npm install -g pm2

# Start with PM2
pm2 start npm --name "qrcode-frontend" -- start
pm2 save
pm2 startup
```

### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/qrcode
```

Add configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /docs {
        proxy_pass http://localhost:8000;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/qrcode /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

## Environment Variables Reference

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Post-Deployment Checklist

- [ ] Database is accessible and populated
- [ ] Backend health check responds: `curl http://your-backend/health`
- [ ] Frontend loads in browser
- [ ] QR code generation works
- [ ] QR code download works
- [ ] Gallery displays properly
- [ ] Delete functionality works
- [ ] CORS is configured correctly
- [ ] SSL certificate is active (production)
- [ ] Database backups are configured
- [ ] Monitoring is set up
- [ ] Error logging is active

## Monitoring & Maintenance

### Backend Logs
```bash
# Systemd logs
sudo journalctl -u qrcode-backend -f

# PM2 logs
pm2 logs qrcode-backend
```

### Frontend Logs
```bash
pm2 logs qrcode-frontend
```

### Database Backup
```bash
# Create backup
pg_dump -U qrcode_user qrcode_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql -U qrcode_user qrcode_db < backup_20260111.sql
```

## Scaling Considerations

- Use load balancer for multiple backend instances
- Implement Redis for caching
- Use CDN for static assets
- Consider database connection pooling
- Set up auto-scaling for traffic spikes

---

Choose the deployment option that best fits your needs and infrastructure!
