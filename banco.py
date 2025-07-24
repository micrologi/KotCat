import sqlite3
import os
from typing import List, Optional, Dict, Any, Tuple
import dotenv

dotenv.load_dotenv('config.env')

class Banco:
    """
    Classe para gerenciar o banco de dados kotcat.db
    """
    
    def __init__(self, db_file: str = os.getenv('PATH_DB')):
        """
        Inicializa a conexão com o banco de dados
        
        Args:
            db_file (str): Caminho para o arquivo do banco de dados
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
    
    def conectar(self):
        """Estabelece conexão com o banco de dados"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def desconectar(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            
    def obter_estados(self) -> List[str]:
        """
        Retorna todos os estados
        """
        if not self.conectar():
            return []

        try:
            self.cursor.execute("""
                SELECT estado FROM cidades 
                GROUP BY estado
                ORDER BY estado
            """)
            resultados = self.cursor.fetchall()
            return [row[0] for row in resultados]
        except Exception as e:
            print(f"❌ Erro ao buscar estados: {e}")
            return []
        finally:
            self.desconectar()
    
    def obter_cidades(self, estado: str) -> List[str]:
        """
        Retorna todas as cidades de um estado
        """
        if not self.conectar():
            return []
        
        try:
            self.cursor.execute("""
                SELECT cidade FROM cidades 
                WHERE estado = ?
                ORDER BY cidade
            """, (estado,))
            resultados = self.cursor.fetchall()
            return [row[0] for row in resultados]
        except Exception as e:
            print(f"❌ Erro ao buscar cidades: {e}")
            return []
        finally:
            self.desconectar()
    
    
    def obter_estados_cidades(self) -> Dict[str, List[str]]:
        """
        Retorna todas as cidades de um estado
        """
        if not self.conectar():
            return {}
        
        estados_cidades = {}
        
        self.cursor.execute("""
            SELECT estado,cidade,latitude,longitude FROM cidades 
            ORDER BY estado,cidade
        """)
        resultados = self.cursor.fetchall()
        estado = ''
        for row in resultados:
            
            if estado != row[0]:
                estado = row[0]
                estados_cidades[estado] = []
            else:
                estados_cidades[estado].append(row[1])            

        return estados_cidades
    
    
    def obter_latitude_longitude(self, cidade: str, estado: str) -> Tuple[float, float]:
        """
        Retorna a latitude e longitude de uma cidade
        """
        if not self.conectar():
            return None
        
        try:
            self.cursor.execute("""
                SELECT latitude,longitude FROM cidades 
                WHERE cidade = ? AND estado = ?
            """, (cidade, estado))
            resultado = self.cursor.fetchone()
            return resultado
        except Exception as e:
            print(f"❌ Erro ao buscar latitude e longitude: {e}")
            return None
        finally:
            self.desconectar()
            
    
    def obter_tipos(self) -> List[str]:
        """
        Retorna todos os tipos de negócios ativos
        
        Returns:
            List[str]: Lista de nomes dos tipos de negócios
        """
        if not self.conectar():
            return []
        
        try:
            self.cursor.execute("""
                SELECT tipo FROM tipos 
                WHERE ativo = 1 
                ORDER BY tipo
            """)
            resultados = self.cursor.fetchall()
            return [row[0] for row in resultados]
        except Exception as e:
            print(f"❌ Erro ao buscar tipos: {e}")
            return []
        finally:
            self.desconectar()
    
    def buscar_tipo(self, id_tipo: int) -> Optional[Dict[str, Any]]:
        """
        Busca um tipo por ID
        
        Args:
            id_tipo (int): ID do tipo
            
        Returns:
            Optional[Dict]: Dados do tipo ou None
        """
        if not self.conectar():
            return None
        
        try:
            self.cursor.execute("""
                SELECT id, tipo, ativo FROM tipos 
                WHERE id = ?
            """, (id_tipo,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                return {
                    "id": resultado[0],
                    "tipo": resultado[1],
                    "ativo": resultado[2]
                }
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar por ID: {e}")
            return None
        finally:
            self.desconectar()
    
    
    def adicionar_tipo(self, tipo: str) -> bool:
        """
        Adiciona um novo tipo de negócio
        
        Args:
            tipo (str): Nome do tipo de negócio
            
        Returns:
            bool: True se adicionado com sucesso
        """
        if not self.conectar():
            return False
        
        try:
            self.cursor.execute("""
                INSERT INTO tipos (tipo, ativo)
                VALUES (?, ?)
            """, (tipo, 1))
            self.conn.commit()
            print(f"✅ Tipo '{tipo}' adicionado com sucesso!")
            return True
        except sqlite3.IntegrityError:
            print(f"⚠️  Tipo '{tipo}' já existe!")
            return False
        except Exception as e:
            print(f"❌ Erro ao adicionar tipo: {e}")
            return False
        finally:
            self.desconectar()
    
    def desativar_tipo(self, id_tipo: int) -> bool:
        """
        Desativa um tipo de negócio
        
        Args:
            id_tipo (int): ID do tipo de negócio
            
        Returns:
            bool: True se desativado com sucesso
        """
        if not self.conectar():
            return False
        
        try:
            self.cursor.execute("""
                UPDATE tipos 
                SET ativo = 0
                WHERE id = ?
            """, (id_tipo,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✅ Tipo ID {id_tipo} desativado com sucesso!")
                return True
            else:
                print(f"⚠️  Tipo ID {id_tipo} não encontrado!")
                return False
        except Exception as e:
            print(f"❌ Erro ao desativar tipo: {e}")
            return False
        finally:
            self.desconectar()
    
    def ativar_tipo(self, id_tipo: int) -> bool:
        """
        Ativa um tipo de negócio
        
        Args:
            id_tipo (int): ID do tipo de negócio
            
        Returns:
            bool: True se ativado com sucesso
        """
        if not self.conectar():
            return False
        
        try:
            self.cursor.execute("""
                UPDATE tipos 
                SET ativo = 1
                WHERE id = ?
            """, (id_tipo,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"✅ Tipo ID {id_tipo} ativado com sucesso!")
                return True
            else:
                print(f"⚠️  Tipo ID {id_tipo} não encontrado!")
                return False
        except Exception as e:
            print(f"❌ Erro ao ativar tipo: {e}")
            return False
        finally:
            self.desconectar()
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do banco de dados
        
        Returns:
            Dict: Estatísticas do banco
        """
        if not self.conectar():
            return {}
        
        try:
            # Total de tipos
            self.cursor.execute("SELECT COUNT(*) FROM tipos")
            total_tipos = self.cursor.fetchone()[0]
            
            # Total de ativos
            self.cursor.execute("SELECT COUNT(*) FROM tipos WHERE ativo = 1")
            total_ativos = self.cursor.fetchone()[0]
            
            # Total de inativos
            self.cursor.execute("SELECT COUNT(*) FROM tipos WHERE ativo = 0")
            total_inativos = self.cursor.fetchone()[0]
            
            # Maior ID
            self.cursor.execute("SELECT MAX(id) FROM tipos")
            max_id = self.cursor.fetchone()[0]
            
            return {
                "total_tipos": total_tipos,
                "total_ativos": total_ativos,
                "total_inativos": total_inativos,
                "max_id": max_id
            }
        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {}
        finally:
            self.desconectar()
