import os
import logging
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from utils import limiter
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from utils import verifica_token, obter_logger_e_configuracao
from routers import llm_router

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o logger da aplicação
logger = obter_logger_e_configuracao()

app = FastAPI(
    title="Trabalho_API_ACD",
    description="""
API dedicada à análise de dados de acidentes e lesões, fundamentada em estatísticas da Administração de Segurança e Saúde Ocupacional (OSHA)*, com integração ao modelo de linguagem via API Groq.  

Oferece dois principais recursos:

- **Grau de Ferimento:**  
  Recebe uma pergunta e fornece uma análise baseada no grau de ferimento, utilizando o banco de dados de lesões da OSHA como referência (Kaggle).

- **Partes do Corpo Afetadas:**  
  Recebe uma pergunta e retorna uma análise sobre as partes do corpo mais suscetíveis a lesões, também alicerçada nos dados da OSHA (Kaggle).

* A OSHA (Occupational Safety and Health Administration) é uma agência do Departamento do Trabalho dos Estados Unidos, responsável pela regulação e fiscalização das condições de saúde e segurança ocupacional.

**Observações de segurança:**
- Autenticação via token simples (API_TOKEN).
- Validação de dados com Pydantic.
- Logs e tratamento de erros com códigos HTTP apropriados.
    """,
    version="1.0.0",
    dependencies=[Depends(verifica_token)],
)


# Permita apenas origens específicas (substitua "https://example.com" pelas origens autorizadas)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
        return JSONResponse(
        status_code=429,
        content={"detail": "Too Many Requests"}
    )

app.add_middleware(SecurityHeadersMiddleware)

# Inclui os endpoints definidos no roteador
app.include_router(llm_router.router)
