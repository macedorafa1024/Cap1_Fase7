# ================================
# FarmTech - Estatísticas em R
# ================================

# --- Dados simulados vindos do Python ---
# Áreas de plantio (em m²)
areas <- c(100, 200, 300, 400, 500)

# Uso de insumos (em litros ou kg)
insumos <- c(50, 75, 120, 90, 60)

# --- Cálculos estatísticos ---
media_area <- mean(areas)
desvio_area <- sd(areas)

media_insumo <- mean(insumos)
desvio_insumo <- sd(insumos)

# --- Resultados ---
cat("=== Estatísticas da Produção ===\n")
cat("Média das áreas de plantio:", media_area, "m²\n")
cat("Desvio padrão das áreas de plantio:", desvio_area, "m²\n\n")

cat("Média do uso de insumos:", media_insumo, "unidades\n")
cat("Desvio padrão do uso de insumos:", desvio_insumo, "unidades\n")

