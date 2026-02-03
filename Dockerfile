# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port (default for Render is 10000 but we'll use $PORT)
EXPOSE 8000

# Start server using uvicorn
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "10000"]
