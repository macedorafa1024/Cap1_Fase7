# FASE 1 - FarmTech Solutions
# Análise estatística dos dados meteorológicos em R
# Executar: Rscript fase1/analise_r.R

library(jsonlite)

# ─── Dados simulados (substituir por leitura do CSV gerado pela API) ────────
set.seed(42)
n_dias <- 90

dados_clima <- data.frame(
  data       = seq(as.Date("2024-10-01"), by = "day", length.out = n_dias),
  temp_max   = rnorm(n_dias, mean = 32, sd = 3),
  temp_min   = rnorm(n_dias, mean = 20, sd = 2),
  precipitacao = rgamma(n_dias, shape = 1.5, rate = 0.3),
  umidade    = rnorm(n_dias, mean = 70, sd = 10)
)

cat("==============================\n")
cat("  ANÁLISE ESTATÍSTICA - SOJA\n")
cat("==============================\n\n")

# Estatísticas descritivas
cat("--- Temperatura Máxima (°C) ---\n")
cat(sprintf("  Média: %.2f\n", mean(dados_clima$temp_max)))
cat(sprintf("  DP:    %.2f\n", sd(dados_clima$temp_max)))
cat(sprintf("  Min:   %.2f\n", min(dados_clima$temp_max)))
cat(sprintf("  Max:   %.2f\n\n", max(dados_clima$temp_max)))

cat("--- Precipitação (mm) ---\n")
cat(sprintf("  Total 90 dias: %.1f mm\n", sum(dados_clima$precipitacao)))
cat(sprintf("  Média diária:  %.2f mm\n", mean(dados_clima$precipitacao)))
cat(sprintf("  Dias com chuva: %d\n\n", sum(dados_clima$precipitacao > 1)))

cat("--- Umidade Relativa (%) ---\n")
cat(sprintf("  Média: %.1f%%\n", mean(dados_clima$umidade)))
cat(sprintf("  Dias abaixo de 60%%: %d\n\n", sum(dados_clima$umidade < 60)))

# Correlação temperatura x precipitação
cor_temp_prec <- cor(dados_clima$temp_max, dados_clima$precipitacao)
cat(sprintf("Correlação Temp x Precipitação: %.3f\n\n", cor_temp_prec))

# Exportar resumo em JSON para o dashboard Python
resumo <- list(
  temp_max_media    = round(mean(dados_clima$temp_max), 2),
  temp_min_media    = round(mean(dados_clima$temp_min), 2),
  precipitacao_total = round(sum(dados_clima$precipitacao), 1),
  precipitacao_media = round(mean(dados_clima$precipitacao), 2),
  umidade_media     = round(mean(dados_clima$umidade), 1),
  dias_analisados   = n_dias,
  correlacao_temp_prec = round(cor_temp_prec, 3)
)

write(toJSON(resumo, auto_unbox = TRUE), "data/analise_r_resultado.json")
cat("Resultado salvo em data/analise_r_resultado.json\n")
