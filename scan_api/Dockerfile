# ============================================================
# Stage 1 — builder: instala dependências Python em /wheels
# ============================================================
FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /wheels

COPY requirements.txt .

# Compila wheels para todas as dependências (evita recompilação no stage final)
RUN pip install --upgrade pip \
    && pip wheel --wheel-dir /wheels -r requirements.txt


# ============================================================
# Stage 2 — runtime: imagem final enxuta e segura
# ============================================================
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Dependências de runtime para OpenCV headless
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para execução segura
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

WORKDIR /app

# Instala wheels do stage anterior (sem reconstruir)
COPY requirements.txt .
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

# Copia código-fonte (após instalar deps para melhor uso do cache do Docker)
COPY --chown=appuser:appgroup . /app/

COPY --chown=appuser:appgroup entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Diretórios de mídia e static com permissões corretas
RUN mkdir -p /app/media /app/staticfiles \
    && chown -R appuser:appgroup /app/media /app/staticfiles

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
