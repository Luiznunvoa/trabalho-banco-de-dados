from sqlalchemy import create_engine, Engine
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Sequence

def conn_db():
    try:
        return create_engine(url ='postgresql+psycopg2://admin:2444@72.60.156.198/banco')
    except Exception as e:
        raise Exception ("Erro ao se conectar com o banco")


def select_db(schema : str, tabela : str, engine : Engine):
    try:
        sql_query = f"SELECT * FROM {schema}.{tabela}" 
        df = pd.read_sql(sql_query, con=engine)
        return df
    except Exception as e:
        raise Exception ("Erro para fazer a query")


def insert_db(session: Session, objs: Sequence[object]):
    try:
        objs = list(objs)

        if len(objs) == 0:
            print("⚠️ Lista vazia: nenhum registro para inserir.")
            return

        session.add_all(objs)
        session.commit()
        tablenames = set(getattr(o, '__tablename__', 'unknown') for o in objs)

        print(f"✅ {len(objs)} registros inseridos com sucesso nas tabelas {', '.join(tablenames)}")

    except SQLAlchemyError as e:
        raise Exception(f"Erro ao inserir no banco: {str(e)}")
    except Exception:
        raise
