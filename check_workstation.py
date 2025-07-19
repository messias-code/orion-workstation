import sys, shutil, os

def comando_existe(comando):
    
    # Verifica se um comando está disponível no sistema.
    # Utiliza which para procurar o comando no PATH do sistema.
    # Retorna True se o comando existir, False caso contrário
    return shutil.which(comando) is not None

def caminho_existe(caminho):

    # Verifica se um caminho (arquivo ou diretório) existe.
    # Expandindo o caminho para o usuário atual, caso seja um caminho relativo.
    # Retorna True se o caminho existir, False caso contrário
    return os.path.exists(os.path.expanduser(caminho))

def verificar(descricao, tipo, valor, condicao):
    
    # Verifica se o comando ou caminho existe e compara com a condição esperada.
    # Se condicao for True, espera que exista; se False, espera que não exista
    if tipo == 'comando':
        encontrado = comando_existe(valor)
    elif tipo == 'caminho':
        encontrado = caminho_existe(valor)
    else:
        encontrado = False

    # Determina o sucesso da verificação com base na condição esperada
    sucesso = (encontrado == condicao)
    
    # Formata o resultado para exibição
    status_str = "✅ SUCESSO" if sucesso else "❌ FALHA"
    detalhe_str = "Encontrado" if encontrado else "Não Encontrado"

    return {'descricao': descricao, 'status': status_str, 'detalhe': detalhe_str}

def exibir_relatorio(titulo, resultados):
    
    # Exibe o relatório de verificação com um título e os resultados formatados
    print(f"\n---- INICIANDO VERIFICAÇÃO DE {titulo} ----")
    print("-" * 76)
    print(f"{'COMPONENTE':<40} | {'STATUS':<13} | {'DETALHE':<15} |")
    print("-" * 76)
    
    # Imprime os resultados de cada verificação
    for i in resultados:
        print(f"{i['descricao']:<40} | {i['status']:<12} | {i['detalhe']:<15} |")

    print("-" * 76)
    print("---- Verificação Concluída ----\n")

def main():
    
    # Verifica se o script foi chamado com os argumentos corretos
    if len(sys.argv) < 2 or sys.argv[1] not in ["install", "rollback"]:
        print("Erro: Você precisa especificar o modo de operação.")
        print(f"Uso: python {sys.argv[0]} [install|rollback]")
        return

    # Armazena o modo de operação
    modo = sys.argv[1]
    # Verifica condição de instalação ou rollback (true para instalação, false para rollback)
    condicao = (modo == "install")
    
    # Define o título com base na condição
    titulo = "INSTALAÇÃO" if condicao else "ROLLBACK (REMOÇÃO)"
    
    # --- Coleta de todos os resultados ---
    resultados_finais = []

    # 1. Zsh e Oh My Zsh
    resultados_finais.append(verificar("Comando 'zsh'", 'comando', 'zsh', condicao))
    resultados_finais.append(verificar("Diretório '~/.oh-my-zsh'", 'caminho', '~/.oh-my-zsh', condicao))
    resultados_finais.append(verificar("Arquivo de config '.zshrc'", 'caminho', '~/.zshrc', condicao))
    resultados_finais.append(verificar("Plugin 'zsh-syntax-highlighting'", 'caminho', '~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting', condicao))

    # 2. Pacotes Opcionais
    resultados_finais.append(verificar("Comando 'nvim' (Neovim)", 'comando', 'nvim', condicao))
    resultados_finais.append(verificar("Comando 'tree'", 'comando', 'tree', condicao))

    # 3. Docker e Docker Compose
    resultados_finais.append(verificar("Comando 'docker'", 'comando', 'docker', condicao))

    # 4. Kubernetes
    resultados_finais.append(verificar("Comando 'kubectl'", 'comando', 'kubectl', condicao))
    resultados_finais.append(verificar("Comando 'helm'", 'comando', 'helm', condicao))
    resultados_finais.append(verificar("Comando 'minikube'", 'comando', 'minikube', condicao))
    resultados_finais.append(verificar("Comando 'k9s'", 'comando', 'k9s', condicao))
    resultados_finais.append(verificar("Repositório APT do K8s", 'caminho', '/etc/apt/sources.list.d/kubernetes.list', condicao))
    
    # 5. Servidores Web
    resultados_finais.append(verificar("Comando 'nginx'", 'comando', 'nginx', condicao))
    resultados_finais.append(verificar("Comando 'apache2'", 'comando', 'apache2', condicao))

    # --- Exibição do Relatório ---
    exibir_relatorio(titulo, resultados_finais)

if __name__ == "__main__":
    main()