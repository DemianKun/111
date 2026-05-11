from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/iot_cocina"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    rol = Column(String(20), default="chef") 

class MedicionReal(Base):
    __tablename__ = "mediciones_sensores"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.datetime.now)
    temp_camara = Column(Float)
    peso_b1 = Column(Float)
    peso_b2 = Column(Float)
    peso_b3 = Column(Float)
    peso_b4 = Column(Float)
    peso_b5 = Column(Float)
    peso_b6 = Column(Float)

class ConfiguracionInventario(Base):
    __tablename__ = "config_inventario"
    id = Column(Integer, primary_key=True, index=True)
    id_bascula = Column(String(20), unique=True)
    nombre_producto = Column(String(100))
    stock_minimo = Column(Float, default=0.5)

class Receta(Base):
    __tablename__ = "recetas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True)
    descripcion = Column(String(255))
    ingredientes_json = Column(JSON) 

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    receta_nombre = Column(String(100))
    empleado_id = Column(Integer, nullable=True)
    estado = Column(String(20), default="PROPUESTA") 
    fecha_asignacion = Column(DateTime, default=datetime.datetime.now)

class RegistroCompra(Base):
    __tablename__ = "registro_compras"
    id = Column(Integer, primary_key=True, index=True)
    producto = Column(String(100))
    telefono_autoriza = Column(String(20))
    fecha_confirmacion = Column(DateTime, default=datetime.datetime.now)
    estado = Column(String(20), default="POR_COMPRAR")

Base.metadata.create_all(bind=engine)