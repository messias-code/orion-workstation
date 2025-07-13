import os
import shutil
import subprocess

# Define cores para a saída no terminal, para ficar mais legível
COR_SUCESSO = '\033[92m'  # Verde
COR_FALHA = '\033[91m'   # Vermelho
COR_RESET = '\033[0m'     # Reseta a cor padrão

def verificar_comando(comando):
    if shutil.which(comando):
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} O comando '{comando}' foi encontrado.")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} O comando '{comando}' NÃO foi encontrado no sistema.")

def verificar_caminho(caminho):
    caminho_expandido = os.path.expanduser(caminho)
    if os.path.exists(caminho_expandido):
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} O caminho '{caminho}' foi encontrado.")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} O caminho '{caminho}' NÃO foi encontrado.")

def main():
    usuario_atual = os.getenv('USER')
    
    if not usuario_atual:
        print(f"{COR_FALHA}Não foi possível determinar o usuário atual. Saindo.{COR_RESET}")
        return

    print("===== INICIANDO VERIFICAÇÃO DE INSTALAÇÃO =====")
    print(f"Verificando como o usuário: {usuario_atual}\n")

    print("--- 1. Ecossistema Kubernetes ---")
    verificar_comando("kubectl")
    verificar_comando("helm")
    verificar_comando("k9s")
    verificar_comando("minikube")
    verificar_caminho("/etc/apt/sources.list.d/kubernetes.list")
    verificar_caminho("/etc/apt/keyrings/kubernetes-apt-keyring.gpg")
    
    comando_dpkg = "dpkg -l | grep -q -E 'kubelet|kubeadm|kubectl'"
    resultado = subprocess.run(comando_dpkg, shell=True)

    if resultado.returncode == 0:
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} Pacotes 'kube...' encontrados via dpkg.")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} Nenhum pacote 'kube...' encontrado via dpkg.")
    print("")

    print("--- 2. Docker ---")
    verificar_comando("docker")
    
    # Verificação do plugin 'docker compose'
    resultado_compose = subprocess.run(["docker", "compose", "version"], capture_output=True)

    if resultado_compose.returncode == 0:
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} O plugin 'docker compose' foi encontrado.")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} O plugin 'docker compose' NÃO foi encontrado.")
        
    # Checagem do serviço systemd
    resultado_servico = subprocess.run(["systemctl", "is-active", "--quiet", "docker.service"])

    if resultado_servico.returncode == 0:
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} O serviço 'docker.service' está ativo (running).")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} O serviço 'docker.service' NÃO está ativo.")
        
    print("*Aviso: a checagem de '/var/lib/docker' pode não ser precisa sem sudo.")
    verificar_caminho("/var/lib/docker")
    print("")

    print("--- 3. Zsh e Shell Padrão ---")
    verificar_comando("zsh")
    verificar_caminho("~/.oh-my-zsh")
    verificar_caminho("~/.zshrc")
    
    comando_shell = ["getent", "passwd", usuario_atual]
    resultado_shell = subprocess.run(comando_shell, capture_output=True, text=True)

    if resultado_shell.returncode == 0 and "/bin/zsh" in resultado_shell.stdout:
        print(f"{COR_SUCESSO}✅ [SUCESSO]{COR_RESET} O shell padrão do usuário '{usuario_atual}' é /bin/zsh.")
    else:
        print(f"{COR_FALHA}❌ [FALHA]{COR_RESET} O shell padrão NÃO foi configurado para /bin/zsh.")
    print("")

    print("===== VERIFICAÇÃO CONCLUÍDA =====")

if __name__ == "__main__":
    main()