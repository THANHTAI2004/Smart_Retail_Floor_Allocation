FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements-lock.txt /app/backend/requirements-lock.txt
RUN pip install --no-cache-dir -r backend/requirements-lock.txt
COPY backend /app/backend
RUN pip install --no-cache-dir --no-deps ./backend
RUN mkdir -p /app/var
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "smart_retail.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
