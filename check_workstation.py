import sys
import shutil
import os
import subprocess

# sys -> para manipulação de argumentos de linha de comando
# shutil -> para verificar a existência de comandos no PATH
# os -> para manipulação de caminhos e verificação de existência de arquivos/diretórios
# subprocess -> para executar comandos do sistema e verificar serviços

# --- Funções de Verificação ---

def comando_existe(comando):
    """Verifica se um comando está disponível no PATH do sistema."""
    return shutil.which(comando) is not None

def caminho_existe(caminho):
    """Verifica se um caminho (arquivo ou diretório) existe."""
    return os.path.exists(os.path.expanduser(caminho))

def servico_existe(servico):
    """Verifica se uma unidade de serviço do systemd existe."""
    try:
        resultado = subprocess.run(
            ['systemctl', 'cat', servico],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return resultado.returncode == 0
    except FileNotFoundError:
        return False

# --- Função de Verificação Principal ---

def verificar(descricao, tipo, valor, condicao):
    """
    Verifica um componente (comando, caminho ou serviço)
    e compara com a condição esperada (instalado ou removido).
    """
    encontrado = False
    if tipo == 'comando':
        encontrado = comando_existe(valor)
    elif tipo == 'caminho':
        encontrado = caminho_existe(valor)
    elif tipo == 'servico':
        encontrado = servico_existe(valor)

    sucesso = (encontrado == condicao)
    status_str = "✅ SUCESSO" if sucesso else "❌ FALHA"
    detalhe_str = "Encontrado" if encontrado else "Não Encontrado"

    return {'descricao': descricao, 'status': status_str, 'detalhe': detalhe_str}

# --- Função de Exibição do Relatório ---

def exibir_relatorio(titulo, resultados):
    """Exibe o relatório de verificação formatado."""
    print(f"\n---- INICIANDO VERIFICAÇÃO DE {titulo} ----")
    print("-" * 90)
    print(f"{'COMPONENTE':<55} | {'STATUS':<13} | {'DETALHE':<15} |")
    print("-" * 90)
    for i in resultados:
        print(f"{i['descricao']:<55} | {i['status']:<12} | {i['detalhe']:<15} |")
    print("-" * 90)
    print("---- Verificação Concluída ----\n")

# --- Função Principal ---

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ["install", "rollback"]:
        print("Erro: Você precisa especificar o modo de operação.")
        print(f"Uso: python3 {sys.argv[0]} [install|rollback]")
        return

    modo = sys.argv[1]
    condicao = (modo == "install")
    titulo = "INSTALAÇÃO" if condicao else "ROLLBACK (REMOÇÃO)"
    
    resultados_finais = []

    # 1. Terminal Moderno (Oh My Zsh)
    resultados_finais.append(verificar("Comando 'zsh'", 'comando', 'zsh', condicao))
    resultados_finais.append(verificar("Diretório '~/.oh-my-zsh'", 'caminho', '~/.oh-my-zsh', condicao))

    # 2. Pacotes Opcionais
    resultados_finais.append(verificar("Comando 'nvim' (Neovim)", 'comando', 'nvim', condicao))
    resultados_finais.append(verificar("Comando 'tree'", 'comando', 'tree', condicao))
    
    # 3. Containerização (Docker)
    resultados_finais.append(verificar("Comando 'docker'", 'comando', 'docker', condicao))
    resultados_finais.append(verificar("Serviço 'docker.service'", 'servico', 'docker.service', condicao))
    resultados_finais.append(verificar("Repositório APT do Docker", 'caminho', '/etc/apt/sources.list.d/docker.list', condicao))

    # 4. Orquestração (Kubernetes)
    resultados_finais.append(verificar("Comando 'kubectl'", 'comando', 'kubectl', condicao))
    resultados_finais.append(verificar("Comando 'minikube'", 'comando', 'minikube', condicao))
    resultados_finais.append(verificar("Repositório APT do Kubernetes", 'caminho', '/etc/apt/sources.list.d/kubernetes.list', condicao))

    # 5. Infraestrutura como Código (IaC)
    resultados_finais.append(verificar("Comando 'terraform'", 'comando', 'terraform', condicao))
    resultados_finais.append(verificar("Repositório do Terraform", 'caminho', '/etc/apt/sources.list.d/hashicorp.list', condicao))
    resultados_finais.append(verificar("Chave GPG do Terraform", 'caminho', '/usr/share/keyrings/hashicorp-archive-keyring.gpg', condicao))
    resultados_finais.append(verificar("Comando 'tofu'", 'comando', 'tofu', condicao))
    resultados_finais.append(verificar("Repositório do OpenTofu", 'caminho', '/etc/apt/sources.list.d/opentofu.list', condicao))
    resultados_finais.append(verificar("Chave GPG 1 do OpenTofu", 'caminho', '/etc/apt/keyrings/opentofu.gpg', condicao))
    resultados_finais.append(verificar("Chave GPG 2 do OpenTofu", 'caminho', '/etc/apt/keyrings/opentofu-repo.gpg', condicao))

    # 6. Ferramentas de Cloud CLI
    resultados_finais.append(verificar("Comando 'az' (Azure CLI)", 'comando', 'az', condicao))
    resultados_finais.append(verificar("Comando 'aws' (AWS CLI)", 'comando', 'aws', condicao))
    resultados_finais.append(verificar("Comando 'gcloud' (Google Cloud CLI)", 'comando', 'gcloud', condicao))
    resultados_finais.append(verificar("Repositório do Google Cloud", 'caminho', '/etc/apt/sources.list.d/google-cloud-sdk.list', condicao))

    exibir_relatorio(titulo, resultados_finais)

if __name__ == "__main__":
    main()