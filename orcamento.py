import polars as pl
import time
import urllib.parse
import requests
import json
import math

def indice_avaliacao(nota: float=3, avaliacoes: int=0)->float:
    
    # Calcula o índice original
    ret = nota * math.log10(avaliacoes + 1)    
    ret = min(100, (ret / 12) * 100)
    
    return round(ret, 2)
    

def pesquisar_negocios(api_key: str, negocio: str = "serralheria", latitude: float = -21.1775, longitude: float = -47.8103, avaliacao_minima: float = 0, mensagem: str = "", raio: int = 13) -> pl.DataFrame:
    url = "https://google.serper.dev/maps"
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "q": negocio,
        "hl": "pt-br",
        "ll": f"@{latitude},{longitude},{raio}z"
    })

    results = requests.request("POST", url, headers=headers, data=payload)    
    locais = results.json().get("places", [])
    
    if not locais:        
        return None
    
    todos_resultados = []
    for lugar in locais:
            
        phone = str(lugar.get("phoneNumber"))
        if (phone == "None" or phone.strip() == ""):
            continue

        website = str(lugar.get("website"))
        if (website == "None" or website.strip() == ""):
            website = ""

        rating = str(lugar.get("rating"))
        if (rating == "None" or rating.strip() == ""):
            rating = 0
        else:
            rating = float(rating)
            
        ratingCount = str(lugar.get("ratingCount"))
        if (ratingCount == "None" or ratingCount.strip() == ""):
            ratingCount = 0
        else:
            ratingCount = int(ratingCount)
            
        avaliacao = indice_avaliacao(rating, ratingCount)
        if (avaliacao < avaliacao_minima):
            continue
                
        dados = {
            "Nome": lugar.get("title"),
            "Endereço": lugar.get("address"),
            "avaliacao": avaliacao,
            "WhatsApp/Fone": phone,
            "Site": website
        }
        todos_resultados.append(dados)

    # Retornar os dados como um DataFrame Polars
    df_ret = pl.DataFrame(todos_resultados)
    
            
    df_ret = df_ret.sort(pl.col("avaliacao"),descending=True)
    
    df_ret = df_ret.with_columns(
        pl.arange(1, 1 + df_ret.height).alias("Id")
    )
    df_ret = df_ret.select(["Id"] + [col for col in df_ret.columns if col != "Id"])
    
    return df_ret