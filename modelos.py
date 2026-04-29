from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///centinela.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

class Alerta(Base):
    __tablename__ = 'alertas'

    id = Column(Integer, primary_key=True)
    fecha_hora = Column(DateTime, default=datetime.datetime.utcnow)
    paciente_id = Column(String)
    nombre = Column(String)
    dni = Column(String)
    edad = Column(String)
    servicio = Column(String)
    cama = Column(String)
    diagnostico = Column(String)
    hallazgos = Column(String)          # separados por coma
    texto_cronologico = Column(Text)    # texto completo analizado
    enviado = Column(Boolean, default=False)

Base.metadata.create_all(engine)