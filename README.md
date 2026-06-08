# FIAP - Faculdade de Informática e Administração Paulista

# FarmTech Solutions - Sistema Integrado de Gestão Agrícola

## 👨‍🎓 Integrantes:
- Rafael Gomes de Macedo - RM566955

## 👩‍🏫 Professores:

### Tutor(a)
- Sabrina Otoni

### Coordenador(a)
- André Godoi

## 📜 Descrição

O projeto **FarmTech Solutions** consolida, na Fase 7, os serviços desenvolvidos ao longo das Fases 1 a 6 em uma única dashboard de gestão agrícola inteligente. A proposta é integrar dados de plantio, clima, sensores IoT, banco de dados, modelos de Machine Learning, alertas em nuvem e visão computacional para apoiar a tomada de decisão no agronegócio.

Na Fase 1, foram implementados cálculos de área de plantio, estimativa de insumos e consulta meteorológica com OpenWeatherMap, além de análise estatística em R. Na Fase 2, os dados foram organizados em uma estrutura relacional, com demonstração local em SQLite e referência ao banco Oracle das fases anteriores. Na Fase 3, sensores IoT simulam leituras de umidade, temperatura, pH, nutrientes, chuva e status de irrigação, representando a automação com ESP32. Na Fase 4, a dashboard integra modelos de regressão com Scikit-Learn para prever umidade futura e rendimento agrícola. Na Fase 5, o sistema implementa alertas usando Amazon SNS, com modo demonstração por log local e registro em banco quando credenciais AWS não estão configuradas. Na Fase 6, há uma camada de visão computacional preparada para YOLO/OpenCV, com fallback simulado para detecção de pragas, doenças ou lavoura saudável.

O resultado é um sistema único em Streamlit, capaz de apresentar indicadores, simular leituras, consultar dados, gerar previsões e sugerir ações corretivas para funcionários da fazenda. A estrutura também pode ser adaptada para outros setores, substituindo os dados e regras de negócio.

## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.env.example</b>: arquivo de exemplo para configurar variáveis de ambiente, como `OPENWEATHER_API_KEY`, `AWS_REGION`, `SNS_TOPIC_ARN` e `AWS_SNS_TOPIC_ARN`.

- <b>.gitignore</b>: define arquivos locais que não devem ser enviados ao GitHub, como `.env`, cache Python, banco SQLite local e logs.

- <b>data</b>: contém a base `dados_agricolas.csv`, modelos treinados (`.pkl`), scalers, banco SQLite local e logs de alerta gerados em modo demonstração.

- <b>fase1</b>: contém os códigos da primeira fase, incluindo cálculo de área, cálculo de insumos, consulta meteorológica, CLI original e scripts R de clima/estatística.

- <b>fase2</b>: contém o módulo de banco de dados relacional em SQLite, com tabelas para talhões, leituras de sensores, irrigações, pragas e alertas.

- <b>fase3</b>: contém a simulação dos sensores IoT, geração do CSV agrícola e lógica de verificação de irrigação.

- <b>fase4</b>: contém o treinamento e carregamento dos modelos de Machine Learning para previsão de umidade futura e rendimento agrícola.

- <b>fase5</b>: contém o serviço de alertas com Amazon SNS, incluindo fallback local quando o ambiente AWS não está configurado.

- <b>fase6</b>: contém a estrutura de visão computacional, preparada para YOLO/OpenCV e com modo simulado para demonstração.

- <b>main_dashboard.py</b>: dashboard principal em Streamlit que integra todas as fases em uma única aplicação.

- <b>requirements.txt</b>: lista de bibliotecas Python necessárias para executar o projeto.

- <b>README.md</b>: arquivo de documentação geral do projeto.

## 🔧 Como executar o código

### Pré-requisitos

- Python 3.10 ou superior.
- VS Code, PyCharm ou outra IDE de preferência.
- Acesso à internet para instalar dependências.
- Conta AWS apenas se desejar testar envio real de alertas via Amazon SNS.
- R instalado apenas se desejar executar manualmente os scripts `.R` da Fase 1.

### Instalação

```bash
git clone https://github.com/macedorafa1024/FarmTech_Fase7.git
cd FarmTech_Fase7
pip install -r requirements.txt
```

### Configuração opcional do ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com os valores desejados:

```bash
OPENWEATHER_API_KEY=sua_chave_openweathermap
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas
# ou
AWS_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas
```

Se as chaves não forem configuradas, o sistema continua funcionando em modo demonstração, usando dados simulados de clima e salvando alertas localmente.

### Execução da dashboard

```bash
streamlit run main_dashboard.py
```

Ao abrir a aplicação, a dashboard apresenta as abas:

- **Visão Geral**: indicadores principais, distribuição de umidade, relação entre umidade e rendimento e rendimento por status de irrigação.
- **Fase 1 - Área & Clima**: cálculo de área, cálculo de insumos, consulta meteorológica e análise estatística em R.
- **Fase 2 - Banco de Dados**: visualização do CSV, importação para SQLite, consultas SQL, talhões, leituras, irrigações e alertas.
- **Fase 3 - Sensores IoT**: simulação de leituras do ESP32 e ativação automática da irrigação.
- **Fase 4 - Machine Learning**: métricas dos modelos, previsão de umidade futura e previsão de rendimento agrícola.
- **Fase 5 - Alertas AWS**: envio de alertas via SNS ou registro local em banco/log.
- **Fase 6 - Visão Computacional**: processamento de imagens da lavoura e detecção simulada ou real de anomalias.

### Configuração do Amazon SNS

1. Acesse o console da AWS.
2. Abra o serviço **SNS**.
3. Crie um tópico Standard chamado `farmtech-alertas`.
4. Crie uma assinatura com protocolo `Email` ou `SMS`.
5. Confirme a assinatura pelo e-mail ou celular.
6. Copie o ARN do tópico para o `.env`.
7. Execute a dashboard e teste a aba **Fase 5 - Alertas AWS**.
