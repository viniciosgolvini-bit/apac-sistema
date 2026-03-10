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

# User-agent genérico para não ser bloqueado
geolocator = Nominatim(user_agent="browser_user_agent_123", timeout=30)

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
        return "<h1>Erro: Arquivo index.html nao encontrado na raiz.</h1>"

@app.post("/calcular-real")
async def calcular_real(dados: DadosRota):
    try:
        # 1. Tenta achar as coordenadas
        loc_o = geolocator.geocode(f"{dados.origem}, Brasil")
        loc_d = geolocator.geocode(f"{dados.destino}, Brasil")
        
        if not loc_o or not loc_d:
            raise HTTPException(status_code=400, detail="GPS nao localizou o endereço.")

        # 2. Motor de Rota Alternativo (Project OSRM Demo)
        url = f"https://router.project-osrm.org/route/v1/driving/{loc_o.longitude},{loc_o.latitude};{loc_d.longitude},{loc_d.latitude}?overview=false"
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                raise HTTPException(status_code=500, detail="Servidor de Mapas Ocupado.")
            res = r.json()

        dist_km = res['routes'][0]['distance'] / 1000
        
        return {
            "distancia": round(dist_km, 1),
            "resultado": {
                "ideal_L": round(dist_km / dados.consumo_kml, 2),
                "total_L": round((dist_km / dados.consumo_kml) * 1.25, 2),
                "economia_perc": "15%"
            },
            "diagnostico_infra": {
                "lat_o": loc_o.latitude, "lon_o": loc_o.longitude,
                "lat_d": loc_d.latitude, "lon_d": loc_d.longitude
            }
        }
    except Exception as e:
        # Isso vai aparecer nos LOGS do Render para voce ver o erro real
        print(f"ERRO CRITICO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
