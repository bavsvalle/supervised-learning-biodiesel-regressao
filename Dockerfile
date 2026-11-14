FROM python:3.11-slim

WORKDIR /app

COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt

COPY src/app_previsao_biodiesel.py src/
COPY outputs/modelo_biodiesel_final.pkl outputs/

WORKDIR /app/src

EXPOSE 8501

CMD ["streamlit", "run", "app_previsao_biodiesel.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
