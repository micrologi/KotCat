from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

class WhatsAppVerifier:
    def __init__(self, headless=False):
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=whatsapp-session")  # Mantém sessão após login
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.logged_in = False

    def login(self):
        print("⏳ Aguardando login no WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        time.sleep(15)  # Aguarda o login via QR Code
        self.logged_in = True

    def verificar_numero(self, numero_completo):
        if not self.logged_in:
            self.login()

        url = f"https://web.whatsapp.com/send?phone={numero_completo}&text&app_absent=0"
        self.driver.get(url)
        print(f"\n🔍 Verificando número: {numero_completo}...")
        time.sleep(10)  # Tempo para a página carregar

        try:
            erro = self.driver.find_element(By.XPATH, "//div[contains(text(), 'número de telefone')]")
            print(f"❌ O número {numero_completo} NÃO tem WhatsApp.")
            return False
        except:
            print(f"✅ O número {numero_completo} TEM WhatsApp.")
            return True

    def fechar(self):
        self.driver.quit()
        print("🔒 Sessão encerrada.")

# Exemplo de uso
if __name__ == "__main__":
    verificador = WhatsAppVerifier()
    verificador.verificar_nu_
