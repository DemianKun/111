import requests
import time

URL_BACKEND = "http://localhost:8000"
URL_BOT = "http://localhost:3000/api/enviar"

def analizar():
    print("🛒 Agente Compras esperando 40s...")
    time.sleep(40)
    alertas_bloqueo = {}

    while True:
        try:
            auth = requests.post(f"{URL_BACKEND}/token", data={"username":"demian_chef","password":"tesi123"}).json()
            headers = {"Authorization": f"Bearer {auth['access_token']}"}
            actual = requests.get(f"{URL_BACKEND}/api/dashboard/mapeado", headers=headers).json()
            
            for item in actual['inventario']:
                nombre, peso = item['nombre'], item['peso']
                if 0.01 < peso <= 0.25 and not alertas_bloqueo.get(nombre):
                    msg = f"⚠️ *ALERTA PARA EL CHEF (9944)*\nStock bajo en: {nombre} ({peso:.2f}kg).\nResponde *OK {nombre}* para pedir."
                    # TIPO 'compras' envía al Chef (9944)
                    requests.post(URL_BOT, json={"tipo": "compras", "mensaje": msg})
                    alertas_bloqueo[nombre] = True
                elif peso > 0.40: alertas_bloqueo[nombre] = False

        except: pass
        time.sleep(5)

if __name__ == "__main__": analizar()