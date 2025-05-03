from fastapi import FastAPI
from app.database import engine
from app.models.produto_movimentacao import Produto  # Importe o modelo
from app.routers import produto
Produto.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API de Estoque"}

# Importe os routers DEPOIS de criar o app
from app.routers import produtos

app.include_router(produtos.router)



