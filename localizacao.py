from streamlit_js_eval import get_geolocation
import os
from typing import List, Dict, Tuple
import dotenv

dotenv.load_dotenv('config.env')

class Localizacao:
    """
    Classe para obter a localização do usuário.
    """
    
    def obter_localizacao(self)-> Tuple[float, float]:
        """
        Obtém a localização do usuário usando Streamlit JS Eval.
        Retorna um dicionário com latitude e longitude.
        """
        location = get_geolocation()
        if location:
            return (
                location['coords']['latitude'],
                location['coords']['longitude']
            )
        else:
            return None
        
