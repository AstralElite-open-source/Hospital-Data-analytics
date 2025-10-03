# Multi-stage build for production optimization
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/exports /app/exports/charts /app/exports/reports \
    /app/data/processed /app/logs /app/admission_hospital_data \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create optimized startup script
COPY --chown=appuser:appuser <<EOF /app/startup.sh
#!/bin/bash
set -e

echo "🏥 Hospital Patient Analytics - Container Starting..."
echo "🔍 Environment: Production"
echo "📁 Working Directory: \$(pwd)"
echo "👤 Running as: \$(whoami)"

# Ensure data directories exist
mkdir -p /app/data/processed /app/exports/charts /app/exports/reports /app/logs

# Run initial analysis (optional, comment out for faster startup)
if [ "\${RUN_INITIAL_ANALYSIS:-false}" = "true" ]; then
    echo "📊 Running initial analysis..."
    python run_analysis.py || echo "⚠️ Analysis completed with warnings, continuing..."
fi

echo "🌐 Starting Streamlit dashboard on port 8501..."
exec streamlit run dashboard/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --browser.gatherUsageStats=false
EOF

RUN chmod +x /app/startup.sh

# Switch to non-root user
USER appuser

# Expose port for Streamlit
EXPOSE 8501

# Health check with proper endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Use exec form for better signal handling
CMD ["/app/startup.sh"]