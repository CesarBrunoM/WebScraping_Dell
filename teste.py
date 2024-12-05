import locale
from datetime import datetime

meses = {
    "janeiro": "January", "fevereiro": "February", "março": "March",
    "abril": "April", "maio": "May", "junho": "June",
    "julho": "July", "agosto": "August", "setembro": "September",
    "outubro": "October", "novembro": "November", "dezembro": "December"
}

# Testando a conversão da data
data_texto = "março 8, 2023"

# Substituir o nome do mês em português para inglês
for mes_pt, mes_en in meses.items():
    data_texto = data_texto.replace(mes_pt, mes_en)

try:
    data = datetime.strptime(data_texto, "%B %d, %Y")
    print("Data convertida:", data)
except ValueError as e:
    print("Erro ao converter data:", e)
