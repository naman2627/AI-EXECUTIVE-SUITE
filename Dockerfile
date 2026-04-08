FROM python:3.11-slim

# Install system dependencies including Node.js to build Vite
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire project
COPY . .

# 1. Build the React frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# 2. Setup Python backend
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 3. Create a non-root user (HuggingFace Spaces requirement)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Expose port exactly as HuggingFace mandates
EXPOSE 7860

# Launch FastAPI, serving the built React assets
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]