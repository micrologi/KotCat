import urllib.parse

mensagem = "Olá, tudo bem? Quero saber mais!"
mensagem_codificada = urllib.parse.quote(mensagem)

print(mensagem_codificada)