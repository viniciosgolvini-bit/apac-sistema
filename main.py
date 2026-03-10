from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from geopy.geocoders import Nominatim
import httpx
import uvicorn
import os
import re

app = FastAPI()

# Configuração de Segurança Simples
ADMIN_PASSWORD = "apac2026" # <--- MUDE SUA SENHA AQUI

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

geolocator = Nominatim(user_agent="apac_logistica_secure_v1", timeout=30)

class DadosRota(BaseModel):
    origem: str
    destino: str
    consumo_kml: float
    password: str # Adicionado para validar no cálculo também

def limpar_endereco(texto: str):
    texto = re.sub(r'[-/]', ' ', texto)
    return f"{texto}, Brasil"

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Erro: Arquivo index.html não encontrado.</h1>"

@app.post("/calcular-real")
async def calcular_real(dados: DadosRota):
    # Valida a senha antes de gastar processamento de GPS
    if dados.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha incorreta.")

    try:
        origem_limpa = limpar_endereco(dados.origem)
        destino_limpa = limpar_endereco(dados.destino)
        
        loc_o = geolocator.geocode(origem_limpa)
        loc_d = geolocator.geocode(destino_limpa)
        
        if not loc_o or not loc_d:
            loc_o = geolocator.geocode(dados.origem.split(',')[0] + ", Brasil")
            loc_d = geolocator.geocode(dados.destino.split(',')[0] + ", Brasil")

        if not loc_o or not loc_d:
            raise HTTPException(status_code=400, detail="GPS não localizou os locais.")

        url = f"https://router.project-osrm.org/route/v1/driving/{loc_o.longitude},{loc_o.latitude};{loc_d.longitude},{loc_d.latitude}?overview=full"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.get(url)
            route = res.json()

        dist_km = route['routes'][0]['distance'] / 1000
        
        return {
            "distancia": round(dist_km, 1),
            "resultado": {
                "ideal_L": round(dist_km / dados.consumo_kml, 2),
                "total_L": round((dist_km / dados.consumo_kml) * 1.25, 2),
                "economia_perc": "15.8%"
            },
            "diagnostico_infra": {
                "lat_o": loc_o.latitude, "lon_o": loc_o.longitude,
                "lat_d": loc_d.latitude, "lon_d": loc_d.longitude
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
