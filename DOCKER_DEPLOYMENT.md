# Docker Container Build and Deployment Guide 🐳

This guide will help you build and push your Hospital Data Analytics container to GitHub Container Registry (GHCR).

## Prerequisites

1. **GitHub Account** with access to your repository
2. **Docker** installed on your local machine
3. **Git** configured with your GitHub credentials

## Option 1: Automated Build with GitHub Actions (Recommended)

### Step 1: Enable GitHub Container Registry

1. Go to your GitHub repository: `https://github.com/AstralElite-open-source/Hospital-Data-analytics`
2. Go to **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**

### Step 2: Push Your Code

The GitHub Actions workflow will automatically trigger when you push to main/master branch:

```bash
git add .
git commit -m "Add Docker container build workflow"
git push origin main
```

### Step 3: Monitor the Build

1. Go to the **Actions** tab in your repository
2. Watch the "Build and Push Docker Image" workflow
3. Once complete, your container will be available at:
   ```
   ghcr.io/astralelite-open-source/hospital-data-analytics:latest
   ```

## Option 2: Manual Build and Push

### Step 1: Login to GitHub Container Registry

```bash
# Create a Personal Access Token (PAT) with 'write:packages' scope
# Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### Step 2: Build the Container

```bash
# Navigate to your project directory
cd "e:\Projects\project - Hospital analytics"

# Build the container
docker build -t ghcr.io/astralelite-open-source/hospital-data-analytics:latest .

# Build with version tag
docker build -t ghcr.io/astralelite-open-source/hospital-data-analytics:v1.0.0 .
```

### Step 3: Push to Registry

```bash
# Push latest version
docker push ghcr.io/astralelite-open-source/hospital-data-analytics:latest

# Push specific version
docker push ghcr.io/astralelite-open-source/hospital-data-analytics:v1.0.0
```

## Option 3: Quick Local Testing

### Test the Container Locally

```bash
# Build and run locally
docker build -t hospital-analytics .

# Run with port mapping
docker run -p 8501:8501 hospital-analytics

# Run with volume mounts for data persistence
docker run -p 8501:8501 \
  -v "./data:/app/data" \
  -v "./exports:/app/exports" \
  hospital-analytics
```

### Access the Application

Once running, access the dashboard at: `http://localhost:8501`

## Container Features

### 🔒 Security Features
- **Non-root user**: Runs as `appuser` for security
- **Multi-stage build**: Smaller production image
- **Minimal dependencies**: Only runtime requirements in final image

### 📊 Application Features
- **Streamlit Dashboard**: Interactive web interface
- **Data Analytics**: Hospital admission analysis
- **Predictive Models**: Capacity and admission forecasting
- **Visualizations**: Charts and geographic mapping

### 🚀 Performance Features
- **Optimized startup**: Fast container initialization
- **Health checks**: Built-in container health monitoring
- **Volume mounts**: Persistent data storage

## Environment Variables

You can customize the container behavior with these environment variables:

```bash
# Run initial analysis on startup (default: false)
docker run -e RUN_INITIAL_ANALYSIS=true -p 8501:8501 hospital-analytics

# Custom Python path
docker run -e PYTHONPATH=/app -p 8501:8501 hospital-analytics
```

## Container Registry Information

### Image Tags Available:
- `latest`: Latest stable version from main branch
- `main`: Latest from main branch
- `develop`: Latest from develop branch
- `v1.0.0`: Specific version releases

### Pull the Container:
```bash
# Pull latest version
docker pull ghcr.io/astralelite-open-source/hospital-data-analytics:latest

# Pull specific version
docker pull ghcr.io/astralelite-open-source/hospital-data-analytics:v1.0.0
```

## Troubleshooting

### Common Issues:

1. **Permission Denied**
   ```bash
   # Make sure you're logged in to GHCR
   docker login ghcr.io
   ```

2. **Build Fails**
   ```bash
   # Check Docker is running
   docker version
   
   # Clean Docker cache
   docker system prune -a
   ```

3. **Application Won't Start**
   ```bash
   # Check logs
   docker logs <container_id>
   
   # Run interactively for debugging
   docker run -it hospital-analytics /bin/bash
   ```

## Production Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  hospital-analytics:
    image: ghcr.io/astralelite-open-source/hospital-data-analytics:latest
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    environment:
      - RUN_INITIAL_ANALYSIS=false
    restart: unless-stopped
```

### Using Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hospital-analytics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hospital-analytics
  template:
    metadata:
      labels:
        app: hospital-analytics
    spec:
      containers:
      - name: hospital-analytics
        image: ghcr.io/astralelite-open-source/hospital-data-analytics:latest
        ports:
        - containerPort: 8501
---
apiVersion: v1
kind: Service
metadata:
  name: hospital-analytics-service
spec:
  selector:
    app: hospital-analytics
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

## Next Steps

1. **Monitor the GitHub Actions**: Check the Actions tab for build status
2. **Test the Container**: Pull and run the container locally
3. **Set up Monitoring**: Add logging and monitoring for production
4. **Configure CI/CD**: Set up automated testing and deployment

For more information, check the [GitHub Container Registry documentation](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).