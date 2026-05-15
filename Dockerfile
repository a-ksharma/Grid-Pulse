FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy project files
COPY . .

EXPOSE 10000

CMD ["uv", "run", "chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "10000"]