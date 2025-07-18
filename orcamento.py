import polars as pl
import time
import urllib.parse
import requests
import json

def pesquisar_negocios(api_key: str, negocio: str = "serralheria", latitude: float = -21.1775, longitude: float = -47.8103, nota_minima: float = 0, mensagem: str = "") -> pl.DataFrame:
    url = "https://google.serper.dev/maps"
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "q": negocio,
        "hl": "pt-br",
        "ll": f"@{latitude},{longitude},13z"
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

        if (nota_minima != 0) and (lugar.get("rating") < nota_minima):
            continue            
        
        website = str(lugar.get("website"))
        if (website == "None" or website.strip() == ""):
            website = ""
        
        #"telefone": "<a href='https://wa.me/5511999999999?text=" + mensagem_codificada + "'</a>",
        
        dados = {
            "Nome": lugar.get("title"),
            "Endereço": lugar.get("address"),
            "Nota": lugar.get("rating"),
            "Avaliações": lugar.get("ratingCount"),
            "WhatsApp/Fone": phone,
            "Site": website
        }
        todos_resultados.append(dados)

    # Retornar os dados como um DataFrame Polars
    df_ret = pl.DataFrame(todos_resultados)
    
    # Considera quem não recebeu avaliações, um mediano
    df_ret = df_ret.with_columns(
        pl.when(pl.col("Nota").is_null())
        .then(3)
        .otherwise(pl.col("Nota"))
        .alias("Nota")
    )            
    
    # Considera quantidade de avaliações 0 quando for null
    df_ret = df_ret.with_columns(
        pl.when(pl.col("Avaliações").is_null())
        .then(0)
        .otherwise(pl.col("Avaliações"))
        .alias("Avaliações")
    )                
            
    df_ret = df_ret.sort(pl.col("Nota") + pl.col("Avaliações"),descending=True)
    
    df_ret = df_ret.with_columns(
        pl.arange(1, 1 + df_ret.height).alias("Id")
    )
    df_ret = df_ret.select(["Id"] + [col for col in df_ret.columns if col != "Id"])
    
    return df_ret