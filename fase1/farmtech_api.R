# FarmTech – API do Clima

if(!require(httr)) install.packages("httr", dependencies=TRUE)
if(!require(jsonlite)) install.packages("jsonlite", dependencies=TRUE)

library(httr)
library(jsonlite)

# Minha chave API do Openweather
api_key <- "a862b6a54e871da45f0f73b15cf95254"

# Cidade que queremos consultar
cidade <- URLencode("Sao Paulo")
pais <- "BR"

# Montar URL da API
url <- paste0("https://api.openweathermap.org/data/2.5/weather?q=",
              cidade, ",", pais, "&appid=", api_key, "&units=metric&lang=pt")

print(url)

# Fazer a requisição à API
resposta <- GET(url)

# Verificar status da requisição (200 = sucesso)
print(status_code(resposta))

# Converter a resposta para JSON
dados <- content(resposta, as = "parsed", encoding = "UTF-8")

# Mostrar os dados principais
# Mostrar os dados principais com explicações
cat("Descrição do clima: ", dados$weather[[1]]$description, "\n")
cat("Temperatura atual: ", dados$main$temp, "°C\n")
cat("Umidade: ", dados$main$humidity, "%\n")
cat("Velocidade do vento: ", dados$wind$speed, "m/s\n")

