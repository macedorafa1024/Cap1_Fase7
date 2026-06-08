import math

# Vetores para armazenar os dados
culturas = []
areas = []
insumos = []

# Função para mostrar o menu na tela
def mostrar_menu():
    print("\n=== MENU PRINCIPAL ===")
    print("1. Inserir cultura")
    print("2. Mostrar culturas")
    print("3. Atualizar cultura")
    print("4. Deletar cultura")
    print("5. Calcular área de plantio")
    print("6. Calcular insumos")
    print("7. Sair")

# Função principal
def main():
    while True:  # Loop infinito até o usuário escolher sair
        mostrar_menu()
        opcao = input("Escolha uma opção: ")

        # Inserir cultura
        if opcao == "1":
            cultura = input("Digite a cultura (milho/soja): ").lower()
            culturas.append(cultura)
            print(f"Cultura {cultura} inserida com sucesso.")

        # Mostrar culturas cadastradas
        elif opcao == "2":
            print("\n=== Culturas cadastradas ===")
            for i, c in enumerate(culturas):
                print(f"{i} - {c}")

        # Atualizar cultura
        elif opcao == "3":
            indice = int(input("Digite o índice da cultura que deseja atualizar: "))
            if 0 <= indice < len(culturas):
                nova_cultura = input("Digite a nova cultura: ").lower()
                culturas[indice] = nova_cultura
                print("Cultura atualizada com sucesso.")
            else:
                print("Índice inválido.")

        # Deletar cultura
        elif opcao == "4":
            indice = int(input("Digite o índice da cultura que deseja deletar: "))
            if 0 <= indice < len(culturas):
                culturas.pop(indice)
                print("Cultura deletada com sucesso.")
            else:
                print("Índice inválido.")

        # Calcular área de plantio
        elif opcao == "5":
            print("\n>> Calcular área de plantio")
            cultura = input("Escolha a cultura (milho/soja): ").lower()

            if cultura == "milho":
                base = float(input("Digite a base do retângulo (m): "))
                altura = float(input("Digite a altura do retângulo (m): "))
                area = base * altura
                areas.append(area)
                print(f"A área de plantio de milho é {area:.2f} m²")

            elif cultura == "soja":
                raio = float(input("Digite o raio da área circular (em metros): "))
                area = math.pi * (raio ** 2)
                areas.append(area)
                print(f"A área de plantio de soja é {area:.2f} m²")

            else:
                print("Cultura inválida. Escolha milho ou soja.")

        # Calcular insumos
        elif opcao == "6":
            print("\n>> Calcular insumos")
            cultura = input("Escolha a cultura (milho/soja): ").lower()
            insumo_nome = input("Digite o nome do insumo (ex: fertilizante, fosfato, herbicida): ")
            quantidade_por_metro = float(input("Digite a quantidade necessária por metro (em litros ou kg): "))
            metros = int(input("Digite o número total de metros da lavoura: "))

            total = quantidade_por_metro * metros
            insumos.append(total)
            print(f"Será necessário {total:.2f} unidades de {insumo_nome} para a cultura {cultura}.")

        # Sair
        elif opcao == "7":
            print("Saindo do programa. Até logo!")
            break

        # Opção inválida
        else:
            print("Opção inválida. Tente novamente.")

# Início do programa
if __name__ == "__main__":
    main()
