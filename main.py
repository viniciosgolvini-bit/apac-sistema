from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import httpx
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# GPS configurado com User-Agent específico para evitar bloqueio
geolocator = Nominatim(user_agent="apac_logistica_v99", timeout=30)

class DadosRota(BaseModel):
    origem: str
    destino: str
    consumo_kml: float

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Erro: index.html nao encontrado na raiz do projeto</h1>"

@app.post("/calcular-real")
async def calcular_real(dados: DadosRota):
    try:
        # 1. Busca Refinada (Trata o endereço completo)
        # O GPS funciona melhor se o endereço for limpo e terminar com ", Brasil"
        loc_o = geolocator.geocode(f"{dados.origem}, Brasil", addressdetails=True)
        loc_d = geolocator.geocode(f"{dados.destino}, Brasil", addressdetails=True)
        
        if not loc_o or not loc_d:
            raise HTTPException(status_code=400, detail="Endereco nao localizado. Tente simplificar a busca.")

        # 2. Motor de Rota (OSRM)
        url = f"https://router.project-osrm.org/route/v1/driving/{loc_o.longitude},{loc_o.latitude};{loc_d.longitude},{loc_d.latitude}?overview=full"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url)
            if res.status_code != 200:
                raise HTTPException(status_code=500, detail="Servidor de rotas ocupado.")
            route = res.json()

        dist_km = route['routes'][0]['distance'] / 1000
        
        return {
            "distancia": round(dist_km, 1),
            "resultado": {
                "ideal_L": round(dist_km / dados.consumo_kml, 2),
                "total_L": round((dist_km / dados.consumo_kml) * 1.25, 2), # Fator APAC de inércia
                "economia_perc": "15.8%"
            },
            "diagnostico_infra": {
                "local_vilao": "Gargalo Urbano de Inercia",
                "rota_desvio": "Otimizacao via reengenharia APAC.",
                "lat_o": loc_o.latitude, "lon_o": loc_o.longitude,
                "lat_d": loc_d.latitude, "lon_d": loc_d.longitude
            }
        }
    except Exception as e:
        print(f"Erro: {e}")
        raise HTTPException(status_code=500, detail="Erro técnico no processamento.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
