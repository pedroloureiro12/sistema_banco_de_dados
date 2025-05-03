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





