import requests
import time

URL_BACKEND = "http://localhost:8000"
URL_BOT = "http://localhost:3000/api/enviar"

def analizar():
    print("🕵️ Agente Vigilante esperando 40s...")
    time.sleep(40)
    estado_prev = None
    
    while True:
        try:
            auth = requests.post(f"{URL_BACKEND}/token", data={"username":"demian_chef","password":"tesi123"}).json()
            headers = {"Authorization": f"Bearer {auth['access_token']}"}
            actual = requests.get(f"{URL_BACKEND}/api/dashboard/mapeado", headers=headers).json()
            
            if estado_prev:
                for i in range(len(actual['inventario'])):
                    p_act = actual['inventario'][i]['peso']
                    p_prev = estado_prev['inventario'][i]['peso']
                    if abs(p_act - p_prev) >= 0.50:
                        msg = f"🕵️ *REPORTE INTERNO (4794)*\nCambio en: {actual['inventario'][i]['nombre']}\nSensor emite: {p_act:.2f}kg"
                        # TIPO 'vigilancia' envía a sí mismo
                        requests.post(URL_BOT, json={"tipo": "vigilancia", "mensaje": msg})
            
            estado_prev = actual
        except: pass
        time.sleep(3)

if __name__ == "__main__": analizar()