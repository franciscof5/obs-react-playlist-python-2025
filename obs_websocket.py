import time
import os
import re
from datetime import datetime
from urllib.parse import urlparse
from obsws_python import ReqClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# ---------------- CONFIGURAÇÕES ---------------- #
REACT_TIME = 10
ARQUIVO_REACTS = "/Users/francisco/Downloads/reacts.txt"
FONTE_TITULO = "ReactTitle"
FONTE_TIMER = "ReactTimer"
DIRETORIO_GRAVACAO = "/Users/francisco/Movies"
TEMPO_CARREGANDO_LINK = 5  # segundos para o react carregar

# Conexão com OBS
client = ReqClient(host="localhost", port=4455, password="123123")

# ---------------- FUNÇÕES ---------------- #

def sanitizar_nome_arquivo(nome: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos"""
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome)
    nome_limpo = nome_limpo.replace(' ', '_')
    nome_limpo = nome_limpo.replace('.', '_')
    return nome_limpo[:100]  # aumenta o limite para caber a URL

def ler_reacts(arquivo: str) -> list:
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reacts = [linha.strip() for linha in f if linha.strip()]
        print(f"✅ {len(reacts)} reacts carregados")
        return reacts
    except Exception as e:
        print(f"❌ Erro ao ler reacts: {e}")
        return []

def configurar_titulo(texto: str):
    try:
        client.set_input_settings(FONTE_TITULO, {"text": texto}, overlay=True)
        print(f"📝 {texto}")
    except:
        pass

def atualizar_timer(segundos: int):
    try:
        minutos = segundos // 60
        segs = segundos % 60
        texto = f"{minutos:02d}:{segs:02d}"
        client.set_input_settings(FONTE_TIMER, {"text": texto}, overlay=True)
    except:
        pass

def formatar_url_para_nome(url: str) -> str:
    """Transforma a URL em formato legível para nome de arquivo"""
    try:
        parsed = urlparse(url)
        dominio = parsed.netloc.split('.')[-2]  # pega 'instagram'
        path = parsed.path.strip('/').replace('/', '-')  # pega o perfil/usuário
        if path:
            return f"{dominio}-{path}"
        return dominio
    except:
        return "link"

def abrir_react(driver, url: str):
    """Abre o link do react na mesma aba"""
    try:
        driver.get(url)
        print(f"🌐 Abrindo: {url}")
        time.sleep(TEMPO_CARREGANDO_LINK)
    except Exception as e:
        print(f"❌ Erro ao abrir link: {e}")

def gravar_react(titulo: str, url: str, tempo_total: int, idx: int):
    """Grava o react e renomeia o arquivo incluindo URL formatada"""
    try:
        print(f"\n🎬 REACT {idx}: {titulo}")

        # Configurar título no OBS
        configurar_titulo(titulo)
        time.sleep(0.5)

        # Parar gravação anterior se existir
        try:
            status = client.get_record_status()
            if status.output_active:
                client.stop_record()
                time.sleep(1)
        except:
            pass

        # Iniciar gravação
        print("⏺️  Iniciando gravação...")
        client.start_record()

        for segundos in range(tempo_total, 0, -1):
            atualizar_timer(segundos)
            time.sleep(1)
            if segundos % 5 == 0 or segundos <= 5:
                print(f"⏰ {segundos}s")

        client.stop_record()
        print("✅ Gravação finalizada")

        # Renomear arquivo mais recente
        arquivos = sorted(
            [f for f in os.listdir(DIRETORIO_GRAVACAO) if f.endswith('.mp4')],
            key=lambda x: os.path.getmtime(os.path.join(DIRETORIO_GRAVACAO, x)),
            reverse=True
        )

        if arquivos:
            arquivo_recente = arquivos[0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            url_formatada = formatar_url_para_nome(url)
            titulo_sanitizado = sanitizar_nome_arquivo(f"{titulo}-{url_formatada}")
            novo_nome = f"{timestamp} - {titulo_sanitizado}.mp4"

            os.rename(
                os.path.join(DIRETORIO_GRAVACAO, arquivo_recente),
                os.path.join(DIRETORIO_GRAVACAO, novo_nome)
            )
            print(f"📁 Renomeado: {arquivo_recente} -> {novo_nome}")

    except Exception as e:
        print(f"❌ Erro: {e}")

# ---------------- MAIN ---------------- #

def main():
    print("🚀 INICIANDO GRAVAÇÃO DE REACTS COM NAVEGADOR")
    print("=" * 60)

    reacts = ler_reacts(ARQUIVO_REACTS)
    if not reacts:
        return

    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("about:blank")  # aba inicial

    try:
        for i, url in enumerate(reacts, 1):
            titulo = f"React_{i}"
            abrir_react(driver, url)
            gravar_react(titulo, url, REACT_TIME, i)
    finally:
        driver.quit()
        print("🌐 Navegador fechado")

    print("\n🎉 GRAVAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Interrompido")
    except Exception as e:
        print(f"💥 Erro: {e}")
    finally:
        try:
            client.disconnect()
        except:
            pass
