import os
import shutil
import subprocess
import sys

# --- CONSTANTES ---
# Define cores para a saída no terminal, para ficar mais legível.
COR_SUCESSO = '\033[92m'  # Verde
COR_FALHA = '\033[91m'    # Vermelho
COR_RESET = '\033[0m'     # Reseta a cor padrão

# --- FUNÇÕES DE VERIFICAÇÃO ---

def verificar_item(descricao, encontrado, deve_existir):
    """
    Função genérica para verificar um item e imprimir o resultado formatado.
    
    Args:
        descricao (str): A descrição do item sendo verificado (ex: "Comando 'kubectl'").
        encontrado (bool): True se o item foi encontrado no sistema, False caso contrário.
        deve_existir (bool): True se o esperado é que o item exista, False caso contrário.
    """
    if encontrado == deve_existir:
        # A condição corresponde ao esperado (ex: devia existir e existe)
        status = f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET}"
        if deve_existir:
            mensagem = "Encontrado como esperado."
        else:
            mensagem = "Removido como esperado."
        print(f"{status} {descricao}: {mensagem}")
    else:
        # A condição é oposta ao esperado (ex: devia existir e não existe)
        status = f"{COR_FALHA}❌ [FALHA]{COR_RESET}"
        if deve_existir:
            mensagem = "NÃO foi encontrado."
        else:
            mensagem = "Ainda existe no sistema."
        print(f"{status} {descricao}: {mensagem}")

def checar_comando_simples(comando, deve_existir):
    """Verifica se um comando existe no PATH do sistema."""
    encontrado = shutil.which(comando) is not None
    verificar_item(f"Comando '{comando}'", encontrado, deve_existir)

def checar_caminho(caminho, deve_existir):
    """Verifica se um arquivo ou diretório existe."""
    caminho_expandido = os.path.expanduser(caminho)
    encontrado = os.path.exists(caminho_expandido)
    verificar_item(f"Caminho '{caminho}'", encontrado, deve_existir)

def checar_comando_subprocess(comando_shell, descricao, deve_existir):
    """Executa um comando no shell e verifica se ele foi bem-sucedido (returncode 0)."""
    # capture_output=True esconde a saída do comando, rodando de forma silenciosa.
    resultado = subprocess.run(comando_shell, shell=True, capture_output=True)
    encontrado = resultado.returncode == 0
    verificar_item(descricao, encontrado, deve_existir)

def checar_shell_padrao(usuario, shell_esperado):
    """Verifica se o shell padrão do usuário é o esperado."""
    comando = ["getent", "passwd", usuario]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    
    descricao = f"Shell padrão do usuário '{usuario}'"
    # Verifica se o comando foi bem-sucedido e se a string do shell esperado está na saída.
    if resultado.returncode == 0 and shell_esperado in resultado.stdout:
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} {descricao} está configurado como '{shell_esperado}'.")
    else:
        shell_atual = resultado.stdout.strip().split(":")[-1]
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} {descricao} NÃO é '{shell_esperado}'. (Atual: {shell_atual})")

# --- FUNÇÃO PRINCIPAL ---

def main():
    """Função principal que orquestra a verificação."""
    # 1. Determina o modo de operação (install ou rollback)
    if len(sys.argv) < 2 or sys.argv[1] not in ["install", "rollback"]:
        print(f"{COR_FALHA}Erro: Você precisa especificar o modo de operação.{COR_RESET}")
        print(f"Uso: python {sys.argv[0]} [install|rollback]")
        return

    modo = sys.argv[1]
    deve_existir = (modo == "install")
    
    # Define o título da verificação dinamicamente
    titulo = "INSTALAÇÃO" if deve_existir else "ROLLBACK (REMOÇÃO)"
    print(f"===== INICIANDO VERIFICAÇÃO DE {titulo} =====")

    usuario_atual = os.getenv('USER')
    if not usuario_atual:
        print(f"{COR_FALHA}Não foi possível determinar o usuário atual. Saindo.{COR_RESET}")
        return
    print(f"Verificando como o usuário: {usuario_atual}\n")

    # --- 2. Inicia as verificações ---
    
    print("--- 1. Ecossistema Kubernetes ---")
    checar_comando_simples("kubectl", deve_existir)
    checar_comando_simples("helm", deve_existir)
    checar_comando_simples("k9s", deve_existir)
    checar_comando_simples("minikube", deve_existir)
    checar_caminho("/etc/apt/sources.list.d/kubernetes.list", deve_existir)
    checar_caminho("/etc/apt/keyrings/kubernetes-apt-keyring.gpg", deve_existir)
    checar_caminho("~/.config/helm", deve_existir)
    checar_comando_subprocess("dpkg -l | grep -q -E 'kubelet|kubeadm|kubectl'", "Pacotes 'kube...' via dpkg", deve_existir)
    print("")

    print("--- 2. Docker ---")
    checar_comando_simples("docker", deve_existir)
    checar_comando_subprocess("docker compose version", "Plugin 'docker compose'", deve_existir)
    # Para o serviço, 'is-active' é o ideal para checar se está rodando no modo 'install'
    # e 'list-units' para ver se foi removido no modo 'rollback'.
    if deve_existir:
        checar_comando_subprocess("systemctl is-active --quiet docker.service", "Serviço 'docker.service' (ativo)", deve_existir)
    else:
        # Se o serviço não existe, `systemctl list-units` terá returncode 1 (falha), o que é o esperado para o rollback.
        # Portanto, invertemos a lógica de sucesso para este caso específico.
        comando_servico = "systemctl list-units --full --all | grep -q 'docker.service'"
        resultado_servico = subprocess.run(comando_servico, shell=True, capture_output=True)
        encontrado = resultado_servico.returncode == 0 # 0 significa que ENCONTROU
        verificar_item("Serviço 'docker.service'", encontrado, deve_existir)

    print("*Aviso: a checagem de '/var/lib/docker' pode exigir privilégios de 'sudo'.")
    checar_caminho("/var/lib/docker", deve_existir)
    print("")

    print("--- 3. Zsh e Shell Padrão ---")
    checar_comando_simples("zsh", deve_existir)
    checar_caminho("~/.oh-my-zsh", deve_existir)
    checar_caminho("~/.zshrc", deve_existir)
    
    # O shell esperado muda dependendo do modo
    shell_esperado = "/bin/zsh" if deve_existir else "/bin/bash"
    checar_shell_padrao(usuario_atual, shell_esperado)
    print("")

    print("===== VERIFICAÇÃO CONCLUÍDA =====")


# --- PONTO DE ENTRADA DO SCRIPT ---
if __name__ == "__main__":
    main()