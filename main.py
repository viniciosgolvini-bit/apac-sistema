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

# GPS com timeout aumentado para conexões lentas
geolocator = Nominatim(user_agent="apac_brazil_final_v50", timeout=30)

# CONFIGURAÇÃO DE API (OpenRouteService é mais estável que OSRM)
ORS_KEY = "from fastapi import FastAPI, HTTPException
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

# GPS com timeout aumentado para conexões lentas
geolocator = Nominatim(user_agent="apac_brazil_final_v50", timeout=30)

# CONFIGURAÇÃO DE API (OpenRouteService é mais estável que OSRM)
ORS_KEY = "COLE_SUA_CHAVE_AQUI"

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
        return "<h1>Erro: index.html nao encontrado</h1>"

@app.post("/calcular-real")
async def calcular_real(dados: DadosRota):
    try:
        # 1. Localização com tratamento de erro
        loc_o = geolocator.geocode(f"{dados.origem}, Brasil")
        loc_d = geolocator.geocode(f"{dados.destino}, Brasil")
        
        if not loc_o or not loc_d:
            raise HTTPException(status_code=400, detail="Endereço não localizado pelo GPS.")

        # 2. Chamada para OpenRouteService (Mais estável e rápido)
        coords = [[loc_o.longitude, loc_o.latitude], [loc_d.longitude, loc_d.latitude]]
        url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={ORS_KEY}&start={loc_o.longitude},{loc_o.latitude}&end={loc_d.longitude},{loc_d.latitude}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url)
            if res.status_code != 200:
                print(f"Erro ORS: {res.text}")
                raise HTTPException(status_code=500, detail="Servidor de rotas fora do ar.")
            route = res.json()

        # Distância vem em metros, convertemos para KM
        dist_km = route['features'][0]['properties']['summary']['distance'] / 1000
        
        return {
            "distancia": round(dist_km, 1),
            "resultado": {
                "ideal_L": round(dist_km / dados.consumo_kml, 2),
                "total_L": round((dist_km / dados.consumo_kml) * 1.25, 2),
                "economia_perc": "15.8%"
            },
            "diagnostico_infra": {
                "local_vilao": "Gargalo por Inércia",
                "rota_desvio": "Reengenharia APAC: Foco em torque constante.",
                "lat_o": loc_o.latitude, "lon_o": loc_o.longitude,
                "lat_d": loc_d.latitude, "lon_d": loc_d.longitude
            }
        }
    except Exception as e:
        print(f"Erro Interno: {e}")
        raise HTTPException(status_code=500, detail="Erro técnico no processamento.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)"

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
        return "<h1>Erro: index.html nao encontrado</h1>"

@app.post("/calcular-real")
async def calcular_real(dados: DadosRota):
    try:
        # 1. Localização com tratamento de erro
        loc_o = geolocator.geocode(f"{dados.origem}, Brasil")
        loc_d = geolocator.geocode(f"{dados.destino}, Brasil")
        
        if not loc_o or not loc_d:
            raise HTTPException(status_code=400, detail="Endereço não localizado pelo GPS.")

        # 2. Chamada para OpenRouteService (Mais estável e rápido)
        coords = [[loc_o.longitude, loc_o.latitude], [loc_d.longitude, loc_d.latitude]]
        url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={ORS_KEY}&start={loc_o.longitude},{loc_o.latitude}&end={loc_d.longitude},{loc_d.latitude}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url)
            if res.status_code != 200:
                print(f"Erro ORS: {res.text}")
                raise HTTPException(status_code=500, detail="Servidor de rotas fora do ar.")
            route = res.json()

        # Distância vem em metros, convertemos para KM
        dist_km = route['features'][0]['properties']['summary']['distance'] / 1000
        
        return {
            "distancia": round(dist_km, 1),
            "resultado": {
                "ideal_L": round(dist_km / dados.consumo_kml, 2),
                "total_L": round((dist_km / dados.consumo_kml) * 1.25, 2),
                "economia_perc": "15.8%"
            },
            "diagnostico_infra": {
                "local_vilao": "Gargalo por Inércia",
                "rota_desvio": "Reengenharia APAC: Foco em torque constante.",
                "lat_o": loc_o.latitude, "lon_o": loc_o.longitude,
                "lat_d": loc_d.latitude, "lon_d": loc_d.longitude
            }
        }
    except Exception as e:
        print(f"Erro Interno: {e}")
        raise HTTPException(status_code=500, detail="Erro técnico no processamento.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
