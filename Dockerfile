FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY Requirements.txt .
RUN pip install --no-cache-dir -r Requirements.txt

# Copy all app files
COPY . .

EXPOSE 10000

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "10000"]