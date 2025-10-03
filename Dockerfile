# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/exports /app/exports/charts /app/exports/reports /app/data/processed /app/logs

# Set permissions
RUN chmod -R 755 /app/exports /app/data /app/logs

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🏥 Hospital Patient Analytics - Starting..."\n\
echo "📊 Running initial analysis..."\n\
python run_analysis.py || echo "⚠️ Analysis completed with warnings, continuing..."\n\
echo "🌐 Starting Streamlit dashboard..."\n\
streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/startup.sh && chmod +x /app/startup.sh

# Run the startup script
CMD ["/app/startup.sh"]