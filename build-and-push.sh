#!/bin/bash

# Hospital Analytics - Docker Build and Push Script
# Usage: ./build-and-push.sh [version]

set -e

# Configuration
REGISTRY="ghcr.io"
REPOSITORY="astralelite-open-source/hospital-data-analytics"
IMAGE_NAME="${REGISTRY}/${REPOSITORY}"

# Get version from parameter or use 'latest'
VERSION=${1:-latest}

echo "🏥 Building Hospital Analytics Container"
echo "========================================"
echo "Registry: ${REGISTRY}"
echo "Repository: ${REPOSITORY}"
echo "Version: ${VERSION}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the container
echo "🔨 Building container..."
docker build -t "${IMAGE_NAME}:${VERSION}" .

# Tag as latest if version is not latest
if [ "${VERSION}" != "latest" ]; then
    echo "🏷️ Tagging as latest..."
    docker tag "${IMAGE_NAME}:${VERSION}" "${IMAGE_NAME}:latest"
fi

# Ask for confirmation to push
echo ""
read -p "🚀 Do you want to push to ${REGISTRY}? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Pushing to registry..."
    
    # Check if logged in to registry
    if ! docker info | grep -q "Username"; then
        echo "🔐 Please login to ${REGISTRY}:"
        echo "   docker login ${REGISTRY}"
        exit 1
    fi
    
    # Push the images
    docker push "${IMAGE_NAME}:${VERSION}"
    
    if [ "${VERSION}" != "latest" ]; then
        docker push "${IMAGE_NAME}:latest"
    fi
    
    echo "✅ Successfully pushed to ${REGISTRY}!"
    echo ""
    echo "🎉 Your container is now available at:"
    echo "   ${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "🚀 To run your container:"
    echo "   docker run -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "🌐 Access your application at: http://localhost:8501"
else
    echo "⏹️ Push cancelled. Container built locally as:"
    echo "   ${IMAGE_NAME}:${VERSION}"
    echo ""
    echo "🚀 To run locally:"
    echo "   docker run -p 8501:8501 ${IMAGE_NAME}:${VERSION}"
fi

echo ""
echo "✨ Build process completed!"