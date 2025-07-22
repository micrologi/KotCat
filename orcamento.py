import polars as pl
import time
import urllib.parse
import requests
import json
import math
from typing import Optional, List, Dict, Any


class Orcamento:
    """
    Classe para gerenciar pesquisas de negócios e automação de contatos.
    
    Esta classe permite:
    - Pesquisar negócios usando a API do Google Serper
    - Calcular índices de avaliação
    - Gerenciar resultados em formato DataFrame
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa a classe Orcamento.
        
        Args:
            api_key (str): Chave da API do Google Serper
        """
        self.api_key = api_key
        self.url_api = "https://google.serper.dev/maps"
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        self.resultados_atuais: Optional[pl.DataFrame] = None
    
    @staticmethod
    def indice_avaliacao(nota: float = 3, avaliacoes: int = 0) -> float:
        """
        Calcula o índice de avaliação baseado na nota e número de avaliações.
        
        Args:
            nota (float): Nota média do estabelecimento (0-5)
            avaliacoes (int): Número de avaliações
            
        Returns:
            float: Índice de avaliação calculado (0-100)
        """
        # Calcula o índice original
        ret = nota * math.log10(avaliacoes + 1)    
        ret = min(100, (ret / 12) * 100)
        
        return round(ret, 2)
    
    def _fazer_requisicao_api(self, negocio: str, latitude: float, longitude: float, raio: int) -> Optional[List[Dict[str, Any]]]:
        """
        Faz a requisição para a API do Google Serper.
        
        Args:
            negocio (str): Tipo de negócio a pesquisar
            latitude (float): Latitude da localização
            longitude (float): Longitude da localização
            raio (int): Raio de busca em km
            
        Returns:
            Optional[List[Dict]]: Lista de locais encontrados ou None se erro
        """
        try:
            payload = json.dumps({
                "q": negocio,
                "hl": "pt-br",
                "ll": f"@{latitude},{longitude},{raio}z"
            })
            
            response = requests.post(self.url_api, headers=self.headers, data=payload)
            response.raise_for_status()
            
            return response.json().get("places", [])
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição da API: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar resposta da API: {e}")
            return None
    
    def _processar_local(self, lugar: Dict[str, Any], avaliacao_minima: float) -> Optional[Dict[str, Any]]:
        """
        Processa um local individual e retorna os dados formatados.
        
        Args:
            lugar (Dict): Dados do local da API
            avaliacao_minima (float): Avaliação mínima para incluir
            
        Returns:
            Optional[Dict]: Dados processados ou None se não atender critérios
        """
        # Processar telefone
        phone = str(lugar.get("phoneNumber", ""))
        if phone == "None" or phone.strip() == "":
            return None
        
        # Processar website
        website = str(lugar.get("website", ""))
        if website == "None" or website.strip() == "":
            website = ""
        
        # Processar rating
        rating_str = str(lugar.get("rating", "0"))
        if rating_str == "None" or rating_str.strip() == "":
            rating = 0.0
        else:
            try:
                rating = float(rating_str)
            except ValueError:
                rating = 0.0
        
        # Processar número de avaliações
        rating_count_str = str(lugar.get("ratingCount", "0"))
        if rating_count_str == "None" or rating_count_str.strip() == "":
            rating_count = 0
        else:
            try:
                rating_count = int(rating_count_str)
            except ValueError:
                rating_count = 0
        
        # Calcular índice de avaliação
        avaliacao = self.indice_avaliacao(rating, rating_count)
        if avaliacao < avaliacao_minima:
            return None
        
        # Retornar dados formatados
        return {
            "Nome": lugar.get("title", ""),
            "Endereço": lugar.get("address", ""),
            "avaliacao": avaliacao,
            "WhatsApp/Fone": phone,
            "Site": website,
            "Rating": rating,
            "Avaliações": rating_count
        }
    
    def pesquisar_negocios(self, 
                          negocio: str = "serralheria", 
                          latitude: float = -21.1775, 
                          longitude: float = -47.8103, 
                          avaliacao_minima: float = 0, 
                          raio: int = 13) -> Optional[pl.DataFrame]:
        """
        Pesquisa negócios na região especificada.
        
        Args:
            negocio (str): Tipo de negócio a pesquisar
            latitude (float): Latitude da localização
            longitude (float): Longitude da localização
            avaliacao_minima (float): Avaliação mínima para incluir resultados
            raio (int): Raio de busca em km
            
        Returns:
            Optional[pl.DataFrame]: DataFrame com os resultados ou None se erro
        """
        print(f"🔍 Pesquisando '{negocio}' na região...")
        
        # Fazer requisição para a API
        locais = self._fazer_requisicao_api(negocio, latitude, longitude, raio)
        
        if not locais:
            print("❌ Nenhum local encontrado ou erro na API")
            return None
        
        print(f"📋 Processando {len(locais)} locais encontrados...")
        
        # Processar cada local
        todos_resultados = []
        for lugar in locais:
            dados_processados = self._processar_local(lugar, avaliacao_minima)
            if dados_processados:
                todos_resultados.append(dados_processados)
        
        if not todos_resultados:
            print("❌ Nenhum local atende aos critérios de avaliação")
            return None
        
        # Criar DataFrame e ordenar
        df_resultados = pl.DataFrame(todos_resultados)
        df_resultados = df_resultados.sort(pl.col("avaliacao"), descending=True)
        
        # Adicionar ID sequencial
        df_resultados = df_resultados.with_columns(
            pl.arange(1, 1 + df_resultados.height).alias("Id")
        )
        df_resultados = df_resultados.select(["Id"] + [col for col in df_resultados.columns if col != "Id"])
        
        # Salvar resultados atuais
        self.resultados_atuais = df_resultados
        
        print(f"✅ Encontrados {len(todos_resultados)} negócios válidos!")
        return df_resultados
    
    def obter_resultados(self) -> Optional[pl.DataFrame]:
        """
        Retorna os resultados da última pesquisa.
        
        Returns:
            Optional[pl.DataFrame]: DataFrame com os resultados ou None
        """
        return self.resultados_atuais
    
    def filtrar_por_avaliacao(self, avaliacao_minima: float) -> Optional[pl.DataFrame]:
        """
        Filtra os resultados atuais por avaliação mínima.
        
        Args:
            avaliacao_minima (float): Avaliação mínima para incluir
            
        Returns:
            Optional[pl.DataFrame]: DataFrame filtrado ou None
        """
        if self.resultados_atuais is None:
            print("❌ Nenhum resultado disponível para filtrar")
            return None
        
        df_filtrado = self.resultados_atuais.filter(pl.col("avaliacao") >= avaliacao_minima)
        
        if df_filtrado.height == 0:
            print(f"❌ Nenhum resultado com avaliação >= {avaliacao_minima}")
            return None
        
        print(f"✅ Filtrados {df_filtrado.height} resultados com avaliação >= {avaliacao_minima}")
        return df_filtrado
    
    def obter_contatos(self) -> List[Dict[str, str]]:
        """
        Retorna lista de contatos dos resultados atuais.
        
        Returns:
            List[Dict]: Lista de dicionários com nome e telefone
        """
        if self.resultados_atuais is None:
            return []
        
        contatos = []
        for row in self.resultados_atuais.iter_rows(named=True):
            contatos.append({
                "nome": row["Nome"],
                "telefone": row["WhatsApp/Fone"],
                "avaliacao": row["avaliacao"]
            })
        
        return contatos
    
    def salvar_resultados(self, arquivo: str = "resultados_negocios.csv"):
        """
        Salva os resultados atuais em arquivo CSV.
        
        Args:
            arquivo (str): Nome do arquivo para salvar
        """
        if self.resultados_atuais is None:
            print("❌ Nenhum resultado para salvar")
            return
        
        try:
            self.resultados_atuais.write_csv(arquivo)
            print(f"✅ Resultados salvos em '{arquivo}'")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
    
    def exibir_resumo(self):
        """
        Exibe um resumo dos resultados atuais.
        """
        if self.resultados_atuais is None:
            print("❌ Nenhum resultado disponível")
            return
        
        print("\n📊 RESUMO DOS RESULTADOS")
        print("=" * 40)
        print(f"Total de negócios: {self.resultados_atuais.height}")
        
        if self.resultados_atuais.height > 0:
            # Estatísticas de avaliação
            avaliacoes = self.resultados_atuais["avaliacao"]
            print(f"Avaliação média: {avaliacoes.mean():.2f}")
            print(f"Melhor avaliação: {avaliacoes.max():.2f}")
            print(f"Pior avaliação: {avaliacoes.min():.2f}")
            
            # Top 3 melhores
            print("\n🏆 TOP 3 MELHORES AVALIADOS:")
            top_3 = self.resultados_atuais.head(3)
            for i, row in enumerate(top_3.iter_rows(named=True), 1):
                print(f"{i}. {row['Nome']} - Avaliação: {row['avaliacao']:.2f}")
        
        print("=" * 40)