import logging, bcrypt, requests, datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from jose import jwt
from pydantic import BaseModel
from typing import Optional, Dict
from ia.ia_vigilante import procesar_lectura_sensores
from ia.ia_asignador import proponer_nueva_comanda
from ia.ia_compras import procesar_respuesta_whatsapp
import database

logging.getLogger("passlib").setLevel(logging.ERROR)
SECRET_KEY = "TESI_INGENIERIA_2026"
app = FastAPI(title="KitchenOS")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- CONFIGURACIÓN DE CONTACTOS ---
NUMERO_CHEF = "5529469944" 
NUMERO_PROVEEDOR = "5564543209"
BOT_URL = "http://localhost:3000/api/enviar"

def get_db():
    db = database.SessionLocal()
    try: yield db
    finally: db.close()

# --- MODELOS ---
class UsuarioCreate(BaseModel): username: str; password: str; rol: Optional[str] = "chef"
class DatosESP32(BaseModel): temp_camara: float; peso_b1: float; peso_b2: float; peso_b3: float; peso_b4: float; peso_b5: float; peso_b6: float
class RecetaCreate(BaseModel): nombre: str; descripcion: str; ingredientes_json: Dict[str, float]
class ConfigUpdate(BaseModel): nombre_producto: str; stock_minimo: float
class TareaProponer(BaseModel): receta_nombre: str
class TareaAceptar(BaseModel): empleado_id: int
class WebhookData(BaseModel): numero: str; texto: str

@app.on_event("startup")
def inicializar_configuracion():
    db = database.SessionLocal()
    if db.query(database.ConfiguracionInventario).count() == 0:
        nombres_base = ["Papas", "Carne", "Tomate", "Cebolla", "Pollo", "Aceite"]
        for i in range(1, 7):
            db.add(database.ConfiguracionInventario(id_bascula=f"peso_b{i}", nombre_producto=nombres_base[i-1], stock_minimo=0.5))
        db.commit()
    db.close()

# --- LOGIN Y REGISTRO ---
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    u = db.query(database.Usuario).filter(database.Usuario.username == form_data.username).first()
    if not u or not bcrypt.checkpw(form_data.password.encode('utf-8'), u.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400)
    return {"access_token": jwt.encode({"sub": u.username}, SECRET_KEY, algorithm="HS256"), "token_type": "bearer", "user_id": u.id, "rol": u.rol}

@app.post("/api/registro")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    existe = db.query(database.Usuario).filter(database.Usuario.username == usuario.username).first()
    if existe: raise HTTPException(status_code=400, detail="El usuario ya existe")
    salt = bcrypt.gensalt(); hashed = bcrypt.hashpw(usuario.password.encode('utf-8'), salt)
    nuevo = database.Usuario(username=usuario.username, password_hash=hashed.decode('utf-8'), rol="cocinero")
    db.add(nuevo); db.commit()
    return {"status": "usuario_creado"}

# --- 1. IA VIGILANTE (Sensores y Alertas) ---
@app.post("/api/sensores")
def recibir_datos(datos: DatosESP32, db: Session = Depends(get_db)):
    ultima_medicion = db.query(database.MedicionReal).order_by(database.MedicionReal.id.desc()).first()
    
    db.add(database.MedicionReal(**datos.model_dump()))
    db.commit()

    configs = db.query(database.ConfiguracionInventario).all()
    mensajes_alerta = []

    # Monitoreo de Temperatura
    if datos.temp_camara > 5.0:
        mensajes_alerta.append(f"❄️ *ALERTA FRÍO*: Temperatura alta ({datos.temp_camara}°C).")

    for config in configs:
        peso_actual = getattr(datos, config.id_bascula)
        peso_anterior = getattr(ultima_medicion, config.id_bascula) if ultima_medicion else peso_actual
        dif = peso_actual - peso_anterior

        # A. Detectar Vacio o Crítico
        if peso_actual <= 0.0:
            mensajes_alerta.append(f"❌ *{config.nombre_producto}* VACÍO (0.0 KG).")
        elif peso_actual <= config.stock_minimo:
            orden_pendiente = db.query(database.RegistroCompra).filter(
                database.RegistroCompra.producto == config.nombre_producto,
                database.RegistroCompra.estado != "COMPLETADA"
            ).first()
            if not orden_pendiente:
                mensajes_alerta.append(f"⚠️ *{config.nombre_producto}* CASI VACÍO ({peso_actual} KG).\nResponde: CONFIRMO {config.nombre_producto}")

        # B. Detectar Reabastecimiento (Llegó el stock)
        if dif >= 0.5:
            mensajes_alerta.append(f"✅ *{config.nombre_producto}* RELLENADO (+{round(dif,2)} KG).")
            ordenes_abiertas = db.query(database.RegistroCompra).filter(
                database.RegistroCompra.producto == config.nombre_producto,
                database.RegistroCompra.estado != "COMPLETADA"
            ).all()
            for orden in ordenes_abiertas:
                orden.estado = "COMPLETADA"
            if ordenes_abiertas:
                db.commit()
                mensajes_alerta.append(f"📦 Orden de {config.nombre_producto} COMPLETADA automáticamente.")
        
        # C. Detectar Consumo Alto (Trazabilidad)
        elif dif <= -0.5:
            mensajes_alerta.append(f"📉 *CONSUMO ALTO*: Se retiraron {round(abs(dif),2)} KG de {config.nombre_producto}.")

    # Disparo de alertas al Chef
    if mensajes_alerta:
        alertas_unidas = "\n".join(mensajes_alerta)
        try:
            requests.post(BOT_URL, json={
                "tipo": "alerta_stock", 
                "mensaje": f"🚨 *VIGILANTE K-OS*\n\n{alertas_unidas}"
            })
        except: pass

    # Reporte de Rutina (Minuto 00)
    ahora = datetime.datetime.now()
    if ahora.minute == 0:
        resumen = f"📊 *INFORME HORARIO*\nTemp: {datos.temp_camara}°C\n"
        for c in configs: resumen += f"- {c.nombre_producto}: {getattr(datos, c.id_bascula)} KG\n"
        try:
            requests.post(BOT_URL, json={"tipo": "alerta_stock", "mensaje": resumen})
        except: pass

    return {"status": "ok"}

# --- DASHBOARD Y CONFIGURACIÓN ---
@app.get("/api/dashboard/mapeado")
def obtener_dashboard_mapeado(db: Session = Depends(get_db)):
    ultima = db.query(database.MedicionReal).order_by(database.MedicionReal.id.desc()).first()
    configs = db.query(database.ConfiguracionInventario).all()
    mapeo = {c.id_bascula: c.nombre_producto for c in configs}
    if not ultima: return {"temperatura": 0, "inventario": []}
    return {
        "fecha": str(ultima.fecha), "temperatura": ultima.temp_camara,
        "inventario": [{"nombre": mapeo.get(f"peso_b{i}", f"B{i}"), "peso": getattr(ultima, f"peso_b{i}")} for i in range(1, 7)]
    }

@app.get("/api/inventario/config")
def obtener_config_lista(db: Session = Depends(get_db)): return db.query(database.ConfiguracionInventario).all()

@app.put("/api/inventario/config/{id_bascula}")
def actualizar_sensor(id_bascula: str, data: ConfigUpdate, db: Session = Depends(get_db)):
    sensor = db.query(database.ConfiguracionInventario).filter(database.ConfiguracionInventario.id_bascula == id_bascula).first()
    if not sensor: raise HTTPException(404)
    sensor.nombre_producto = data.nombre_producto; sensor.stock_minimo = data.stock_minimo
    db.commit(); return {"status": "actualizado"}

# --- RECETAS ---
@app.get("/api/recetas")
def listar_recetas(db: Session = Depends(get_db)): return db.query(database.Receta).all()

@app.post("/api/recetas")
def guardar_receta(receta: RecetaCreate, db: Session = Depends(get_db)):
    db.add(database.Receta(**receta.model_dump())); db.commit()
    return {"status": "receta_guardada"}

# --- 2. IA DE ASIGNACIÓN (Tareas) ---
@app.get("/api/tareas/propuestas")
def obtener_propuestas(db: Session = Depends(get_db)): return db.query(database.Tarea).filter(database.Tarea.estado == "PROPUESTA").all()

@app.get("/api/tareas/activas")
def obtener_tareas_activas(db: Session = Depends(get_db)):
    tareas = db.query(database.Tarea).filter(database.Tarea.estado.in_(["PENDIENTE", "EN_PROCESO"])).all()
    res = []
    for t in tareas:
        u = db.query(database.Usuario).filter(database.Usuario.id == t.empleado_id).first()
        res.append({"id": t.id, "receta": t.receta_nombre, "estado": t.estado, "cocinero": u.username if u else "---"})
    return res

@app.post("/api/tareas/proponer")
def proponer_tarea(data: TareaProponer, db: Session = Depends(get_db)):
    existe = db.query(database.Tarea).filter(database.Tarea.receta_nombre == data.receta_nombre, database.Tarea.estado.in_(["PROPUESTA", "PENDIENTE", "EN_PROCESO"])).first()
    if existe: return {"status": "ya_existe"}
    
    nueva = database.Tarea(receta_nombre=data.receta_nombre, estado="PROPUESTA", empleado_id=None)
    db.add(nueva); db.commit()
    
    # Python dispara la propuesta al Grupo de WhatsApp
    try:
        requests.post(BOT_URL, json={
            "tipo": "propuesta",
            "mensaje": f"👨‍🍳 *COMANDA K-OS*\nHay que preparar: *{data.receta_nombre}*.\n¿Quién la toma? Respondan *YO* o *ACEPTO*."
        })
    except: pass
    return {"status": "propuesta_lanzada", "id": nueva.id}

@app.put("/api/tareas/aceptar/{tarea_id}")
def aceptar_tarea(tarea_id: int, data: TareaAceptar, db: Session = Depends(get_db)):
    tarea = db.query(database.Tarea).filter(database.Tarea.id == tarea_id, database.Tarea.estado == "PROPUESTA").first()
    if not tarea: raise HTTPException(404)
    tarea.empleado_id = data.empleado_id; tarea.estado = "PENDIENTE"; db.commit()
    return {"status": "aceptada"}

@app.get("/api/estadisticas/avanzadas")
def obtener_estadisticas(db: Session = Depends(get_db)):
    mediciones = db.query(database.MedicionReal).order_by(database.MedicionReal.id.desc()).limit(10).all()
    if not mediciones: return {"labels": [], "data": []}
    mediciones.reverse()
    return {"labels": [m.fecha.strftime("%H:%M:%S") for m in mediciones], "data": [m.peso_b1 for m in mediciones]}

# --- 3. IA DE COMPRAS Y ESCUCHA (Webhook) ---
@app.post("/api/whatsapp/webhook")
def whatsapp_webhook(data: WebhookData, db: Session = Depends(get_db)):
    texto = data.texto.upper().strip()
    
    # Si Chef confirma compra
    if texto.startswith("CONFIRMO "):
        producto = texto[9:].strip()
        db.add(database.RegistroCompra(producto=producto, telefono_autoriza=data.numero))
        db.commit()
        try:
            requests.post(BOT_URL, json={
                "tipo": "orden_compra",
                "mensaje": f"🛒 *ORDEN DE COMPRA K-OS*\nEl Chef autorizó reabastecer: *{producto}*.\nFavor confirmar recepción."
            })
        except: pass
        return {"status": "comprado"}
        
    # Si Cocinero acepta tarea en el grupo
    elif texto in ["ACEPTO", "YO"]:
        print(f"👨‍🍳 Cocinero desde {data.numero} aceptó la tarea vía WhatsApp.")
        return {"status": "cocinero_aviso"}

    return {"status": "recibido"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)