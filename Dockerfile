FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Hugging Face Spaces runs on port 7860
ENV PORT=7860
ENV CHAINLIT_PORT=7860

# Required for Chainlit on HF Spaces
ENV CHAINLIT_AUTH_SECRET=$CHAINLIT_AUTH_SECRET
ENV OAUTH_GOOGLE_CLIENT_ID=$OAUTH_GOOGLE_CLIENT_ID
ENV OAUTH_GOOGLE_CLIENT_SECRET=$OAUTH_GOOGLE_CLIENT_SECRET

EXPOSE 7860

CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]