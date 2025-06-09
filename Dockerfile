FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set workdir
WORKDIR /app

# Copy toàn bộ source vào image
COPY . .

# Cài thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Mở port
EXPOSE 8001

# Lệnh khởi động app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
