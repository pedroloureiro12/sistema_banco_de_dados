from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Optional
from app.models.produto_movimentacao import Produto
from app.models.produto_movimentacao import Movimentacao
from app.schemas.produto_movimentacao import ProdutoBase, MovimentacaoBase
from app.database import get_session

router = APIRouter(prefix="/produtos", tags=["produtos"])

def get_produto(produto_id: int, session:Session)-> Optional[Produto]:
    query = select(Produto).where(Produto.id == produto_id)
    return session.scalars(query).first()

def produto_existe(produto_id: int,session: Session) -> bool:
    result = get_produto(produto_id, session)
    return result is not None


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto: ProdutoBase,
    session: Session = Depends(get_session),
):
    query= select(Produto).where(Produto.nome == produto.nome)
    if session.scalars(query).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="produto ja existente.",
        )
    novo_produto = Produto(nome=produto.nome, descricao=produto.descricao)
    session.add(novo_produto)
    session.commit()
    session.refresh(novo_produto)   
    return {"message": "Produto criado com sucesso", "produto": novo_produto}
@router.get("/{produto_id}")
async def ler_produto(
    nome:str,
    session: Session= Depends(get_session)
):
    produto= session.query(Produto).filter(Produto.nome == nome).first()
    if not produto:
        raise HTTPException(
	    status.HTTP_404_NOT_FOUND,
	    detail= "produto nao encontrado"
        )
    return produto

@router.post("/movimentacoes", status_code = status.HTTP_201_CREATED)
async def criar_movimentacao(
    movimentacao: MovimentacaoBase,
    session: Session= Depends(get_session),
):
    if not produto_existe(movimentacao.produto_id, session):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Produto nao enontrado"
        )

    nova_movimentacao = Movimentacao(**movimentacao.model_dump())
    session.add(nova_movimentacao)
    session.commit()

    entrada = session.scalar(
        select(func.sum(Movimentacao.quantidade))
            .where(
                Movimentacao.produto_id == movimentacao.produto_id,
                Movimentacao.tipo == "entrada"
        )
    ) or 0
    
    saida = session.scalar(
            select(func.sum(Movimentacao.quantidade))
        .where(
                Movimentacao.produto_id == movimentacao.produto_id,
               Movimentacao.tipo == "saida"
	)
    ) or 0

    return {
       	"produto_id": movimentacao.produto_id,
        "total_entrada": entrada,
        "total_saida": saida,

    }
@router.get("/{produto_id}/estoque")
async def consultar_estoque(produto_id: int, session: Session = Depends(get_session)):
    produto = get_produto(produto_id, session)
    if not produto:
        raise HTTPException(
	    status.HTTP_404_NOT_FOUND, detail="Produto não encontrado"
	)
    entrada = session.scalar(
    	select(func.sum(Movimentacao.quantidade))
        .where(Movimentacao.produto_id == produto_id, Movimentacao.tipo == "entrada")
    ) or 0


    saida = session.scalar(
        select(func.sum(Movimentacao.quantidade))
        .where(Movimentacao.produto_id == produto_id, Movimentacao.tipo == "saida")
    ) or 0

    saldo = entrada - saida

    return {
        "produto_id": produto_id,
        "o estoque tem o total de": saldo
    }

@router.get("/{produto_id/movimentacoes")
async def consultar_movimentacoes(produto_id:int, session: Session = Depends(get_session)):
    produto = get_produto(produto_id, session)
    if not produto:
        raise HTTPException(
    		status.HTTP_404_NOT_FOUND, detail = "produto nao encontrado"
	)
    movimentacoes = session.execute(
	select(Movimentacao).where(Movimentacao.produto_id == produto_id)
    ).scalars().all()

    return movimentacoes

