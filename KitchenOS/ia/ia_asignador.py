import requests
import time

URL_BACKEND = "http://localhost:8000"
URL_BOT = "http://localhost:3000/api/enviar"

def iniciar_autonomia():
    print("🤖 [K-OS] Agente Asignador Autónomo Iniciado...")
    print("Modo: SUGERENCIA (Las tareas se lanzan al aire para ser aceptadas)")
    time.sleep(5) 

    while True:
        try:
            # 1. Autenticación
            auth = requests.post(f"{URL_BACKEND}/token", data={"username":"demian_chef", "password":"tesi123"}).json()
            headers = {"Authorization": f"Bearer {auth.get('access_token', '')}"}

            if not auth.get('access_token'):
                print("⚠️ Error de autenticación. Reintentando en 10s...")
                time.sleep(10)
                continue

            # 2. Obtener datos clave: Stock y Recetas
            # ¡Ya no necesitamos la lista de cocineros aquí!
            req_stock = requests.get(f"{URL_BACKEND}/api/dashboard/mapeado", headers=headers).json()
            stock_actual = req_stock.get('inventario', [])
            recetas = requests.get(f"{URL_BACKEND}/api/recetas", headers=headers).json()

            dict_stock = {item['nombre']: item['peso'] for item in stock_actual}
            print(f"\n🔍 Analizando viabilidad... (Stock actual vs {len(recetas)} recetas)")

            for receta in recetas:
                ingredientes_req = receta.get('ingredientes_json', {}) 
                
                if not ingredientes_req or not isinstance(ingredientes_req, dict):
                    continue

                puede_cocinar = True
                
                for ingrediente, cantidad_necesaria in ingredientes_req.items():
                    peso_disponible = dict_stock.get(ingrediente, 0.0)
                    if peso_disponible < float(cantidad_necesaria):
                        puede_cocinar = False
                        break 
                
                if puede_cocinar:
                    # En lugar de asignar, lanzamos la PROPUESTA al backend
                    payload_propuesta = {
                        "receta_nombre": receta['nombre']
                    }
                    
                    res = requests.post(
                        f"{URL_BACKEND}/api/tareas/proponer",
                        json=payload_propuesta,
                        headers=headers
                    )
                    
                    res_json = res.json()
                    
                    # Si el backend confirma que es una propuesta nueva (que nadie más está cocinando ya)
                    if res.status_code == 200 and res_json.get("status") == "propuesta_lanzada":
                        msg_whatsapp = (
                            f"📢 *NUEVA PROPUESTA DE COCINA*\n"
                            f"¡Tenemos stock suficiente para preparar *{receta['nombre']}*!\n"
                            f"👨‍🍳 _El primer cocinero en aceptar tomará la orden._\n"
                            f"Ingresa al K-OS Dashboard para aceptar."
                        )
                        
                        try:
                            requests.post(URL_BOT, json={"tipo": "propuesta", "mensaje": msg_whatsapp})
                        except:
                            pass

                        print(f"✅ ¡Propuesta lanzada al aire! Receta: '{receta['nombre']}'")
                    
                    elif res.status_code == 200 and res_json.get("status") == "ya_existe":
                        # Si ya se propuso antes o alguien la está cocinando, simplemente la saltamos
                        pass

        except Exception as e:
            print(f"❌ Error de conexión o ejecución: {e}")
        
        time.sleep(30) 

if __name__ == "__main__":
    iniciar_autonomia()