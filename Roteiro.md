# Roteiro de Desenvolvimento Backend

# 1. Configurando Ambiente de Trabalho

Crie o ambiente virtual digitando os seguintes codigos no terminal:
    
  ```bash
    mkdir company_app
    cd company_app
    python3 -m venv .venv
  ```
    
Ative o ambiente virtual:
    
  ```bash
    source .venv/bin/activate
  ```
# 2. Instalando Dependências:

```bash
pip install "fastapi[standard]"
pip install pydantic_settings
```
Instale o SQLAlchemy para conexão com o banco de dados e pydantic_settings para configurações de variáveis de ambiente.

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config
```
```bash
pip install SQLAlchemy
pip install mysqlclient
```
# 3 Comçando pelo diretorio app
```bash
mkdir app
touch app/__init__.py app/main.py app/database.py
```
No arquivo main.py adicionamos o seguinte codigo 

```python
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
```
No arquivo database.py adicionaremos

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.settings.config import Settings


settings = Settings()

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{settings.db_user}:"
    f"{settings.db_pass}@"
    f"{settings.db_host}:"
    f"{settings.db_port}/"
    f"{settings.db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


SessionLocal = sessionmaker(autoflush=False, bind=engine)


Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
# 4 Rotas
Ultilizaremos no API o conceito basico de rotas para o funcionamento do projeto, usando  os seguintes ccomandos abaixo para criar a pasta `routers` e o arquivo `produtos.py` :

```bash
mkdir app/routers
touch app/routers/produtos.py
```
Dentro do arquivo produtos.py será adicionado o seguinte

```python
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
```
# 5. Banco de Dados

O projeto usara o 'docker' para o banco de dados mySQL, se o docker esta instalado podemos executar comtendo 'mysql' usando o comando


```bash
docker run --name=sistema_teste_db_container --restart on-failure -p 3306:3306 -d mysql/mysql-server
```

 para funcionar o container, preciasamos de senha gerada para o usuário `root`.

```bash
docker logs company_db_container 2>&1 | grep GENERATED
```

Copie a root password que apareceu e salve ela.

Agora vamos alterar a senha do usuário `root`, basta executar o comando abaixo e depois colar a senha que você copiou acima:

```bash
docker exec -it company_db_container mysql -uroot -p
```

Execute os comando SQL para alterar a senha, permitir a conexão com um *visual tool* e já aproveite para criar o banco que vamos utilizar:

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '<nova-senha>';
UPDATE mysql.user SET host = '%' WHERE user='root';
CREATE DATABASE <nome-banco>;
quit
```

Depois disso, aperte CTRL+D para sair e execute:

```bash
docker restart company_db_container
```
# 6. Settings

Para que nosso código possa se conectar ao banco de dados que criamos, precisamos passar informações que ficam no diretorio settings



Use os comandos abaixo no terminal linux para realizar a montagem dos arquivos.

```bash
mkdir app/settings
cd app/settings
touch .env config.py 
```

</aside>

Começando por `config.py` temos:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	model_config= SettingsConfigDict(env_file="app/settings/.env")
	
	db_user: str
	db_pass: str
	
	db_host: str
	db_port: int
	db_name: str
```

Agora vamos configurar o arquivo `.env` para colocar as informações dos bancos de dados.

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=<senha-que-você-configurou>
DB_NAME=<nome-que-você-deu-ao-banco>
```

# 7. Models

As `models` são uma representação, com classes, de uma tabela do banco de dados. para realizar o objetivo do teste, primeiro criamos o diretorio `models` e adicionaremos o arquivo `produto_movimentacao.py`


```bash
mkdir app/models
touch app/models/produto_movimentacao.py
```
E agora podemos editar nosso `models/produto_movimentacao.py`:

```python
# app/models/produto_movimentacao.py
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.settings.database import Base
from enum import Enum as PyEnum
import datetime


class Produto(Base):
        __tablename__="produtos"

        id: Mapped[BigInteger] = mapped_column(
                BigInteger,
                primary_key= True,
                autoincrement=True,
        )

        nome: Mapped[String]= mapped_column(String(50), nullable = False)
        descricao:Mapped[String]= mapped_column(String(200),nullable=True)

class TipoDeMovimento(PyEnum):
        ENTRADA = "entrada"
        SAIDA= "saida"



class Movimentacao(Base):
        __tablename__="movimentacao"

        id: Mapped[BigInteger] = mapped_column(
                BigInteger,
                primary_key= True,
                autoincrement= True,
                index = True,
        )

        quantidade: Mapped[Integer]= mapped_column(Integer)
        produto_id: Mapped[Integer]=mapped_column(ForeignKey("produtos.id"),nullable=False)
        tipo: Mapped[TipoDeMovimento] = mapped_column(Enum(TipoDeMovimento),nullable=False)
        data: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, nullable=False)





```

Note que ainda estão faltando alguns atributos da classe, ou linhas da nossa tabela a serem implementados. Seguindo o exemplo acima, preencha os atributos que estão faltando.

# 8. Alembic

Para facilitar a criação da tabela `produto_movimentacao.py` no banco de dados vamos utilizar a biblioteca Alembic

Primeiro, instale e inicie a biblioteca no diretório raiz da aplicação:

```bash
# ~/sistema_teste$
pip install alembic
alembic init alembic
```


 passando para as configurações do Alembic, modificamos o arquivo env.py, adicionando as seguintes linhas de codigos abaixo.
 
```python
# ~/sistema_teste/alembic/env.py

#  ... código omitido

# from alembic import context

from app.settings.database import SQLALCHEMY_DATABASE_URL

# ... código omitido 

#config = context.config

config.set_main_option(
    "sqlalchemy.url",
    SQLALCHEMY_DATABASE_URL,
)

#target_metadata = None

from app.models import company
target_metadata = company.Base.metadata

# ... código omitido 
```

Depois disso, vamos gerar uma migration automaticamente, execute o comando abaixo a partir da raiz do projeto:

```bash
alembic revision --autogenerate -m "initial" --rev-id 1
```

Para criar as tabelas no banco de acordo com a revision gerada, execute o comando abaixo:

```bash
alembic upgrade head
```

# 9. Schemas
Os schemas são formas da nossa aplicação dizer o que ela espera receber e o que ela vai responder, primeiro vamos criar a pasta e o arquivo dentro dessa pasta:

```bash
mkdir app/schemas
touch app/schemas/produto_movimentacao.py
```
Agora podemos editar nosso arquivo com o código abaixo:

```python
#app/schemas/produto_movimentacao.py
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
````

# 10. Executando

Como já adicionamos as funções no arquivo produto_movimentacao.py no topico Routers, podemos executar o projeto para verificar as suas funcionalodades. Utilizando o comando para comecar a execução do projeto:

```bash
fastapi dev app/main.py
```


caso o projeto não tenha a iniciação correta, verifique se o  ambiente virtual do python ativo, para isso, use o comando baixo para ativar o `venv` antes de chamar o `fastapi`:

```bash
source .venv/bin/activate
```
Agora, acesse o endereço indicado no output do `fastapi`, por padrão é o http://127.0.0.1:8000/docs, e acesso a aplicação documentada com o Swagger UI para testar as rotas da sua nova API.
