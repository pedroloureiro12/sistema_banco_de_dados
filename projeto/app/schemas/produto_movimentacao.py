from pydantic import BaseModel
from datetime import datetime
from enum import Enum

 
class ProdutoBase(BaseModel):
	nome: str
	descricao: str

class ProdutoCriado(ProdutoBase):
	pass

class Produto(ProdutoBase):
	id: int
	
	class Config:
		from_attributes = True

class MovimentacaoBase(BaseModel):
	quantidade : int
	produto_id: int
	tipo: str

class MovimentacaoCriado(MovimentacaoBase):
	pass


class movimentacao(MovimentacaoBase):
	id: int
	data: datetime
	
	class Config:
		from_attributes= True



class SaldoProduto(BaseModel):
	produto_id: int
	total_entrada: int
	total_saida: int
	saldo: int

