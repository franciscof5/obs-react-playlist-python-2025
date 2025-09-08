import time
import os
import re
from datetime import datetime
from obsws_python import ReqClient

# ---------------- CONFIGURAÇÕES ---------------- #
REACT_TIME = 10  # duração de cada react em segundos
ARQUIVO_REACTS = "/Users/francisco/Downloads/reacts.txt"
FONTE_TITULO = "ReactTitle"
FONTE_TIMER = "ReactTimer"
DIRETORIO_GRAVACAO = "/Users/francisco/Movies"

# Conexão com o OBS
client = ReqClient(host="localhost", port=4455, password="123123")

# ---------------- FUNÇÕES ---------------- #

def sanitizar_nome_arquivo(nome: str) -> str:
    """Remove caracteres inválidos para nome de arquivo"""
    nome_limpo = re.sub(r'[<>:"/\\|?*]', '', nome)
    nome_limpo = nome_limpo.replace(' ', '_')
    nome_limpo = nome_limpo.replace('.', '_')
    return nome_limpo[:40]

def ler_reacts(arquivo: str) -> list:
    """Lê os reacts do arquivo TXT"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reacts = [linha.strip() for linha in f if linha.strip()]
        print(f"✅ {len(reacts)} reacts carregados")
        return reacts
    except Exception as e:
        print(f"❌ Erro ao ler reacts: {e}")
        return []

def configurar_titulo(texto: str):
    """Atualiza a fonte de título na cena"""
    try:
        client.set_input_settings(FONTE_TITULO, {"text": texto}, overlay=True)
        print(f"📝 {texto}")
    except:
        pass

def atualizar_timer(segundos: int):
    """Atualiza a fonte do timer na cena"""
    try:
        minutos = segundos // 60
        segs = segundos % 60
        texto = f"{minutos:02d}:{segs:02d}"
        client.set_input_settings(FONTE_TIMER, {"text": texto}, overlay=True)
    except:
        pass

def gravar_react(titulo: str, tempo_total: int, idx: int):
    """Grava um react e renomeia o arquivo com sufixo do TXT"""
    try:
        print(f"\n🎬 REACT {idx}: {titulo}")

        # 1. Configurar título
        configurar_titulo(titulo)
        time.sleep(0.5)

        # 2. Parar gravação anterior se existir
        try:
            status = client.get_record_status()
            if status.output_active:
                client.stop_record()
                time.sleep(1)
        except:
            pass

        # 3. Iniciar gravação
        print("⏺️  Iniciando gravação...")
        client.start_record()

        # 4. Timer regressivo
        for segundos in range(tempo_total, 0, -1):
            atualizar_timer(segundos)
            time.sleep(1)
            if segundos % 5 == 0 or segundos <= 5:
                print(f"⏰ {segundos}s")

        # 5. Parar gravação
        client.stop_record()
        print("✅ Gravação finalizada")

        # 6. Renomear arquivo mais recente
        arquivos = sorted(
            [f for f in os.listdir(DIRETORIO_GRAVACAO) if f.endswith('.mp4')],
            key=lambda x: os.path.getmtime(os.path.join(DIRETORIO_GRAVACAO, x)),
            reverse=True
        )

        if arquivos:
            arquivo_recente = arquivos[0]
            timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            titulo_sanitizado = sanitizar_nome_arquivo(titulo)
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
    print("🚀 INICIANDO GRAVAÇÃO (MÉTODO SIMPLES)")
    print("=" * 60)

    reacts = ler_reacts(ARQUIVO_REACTS)
    if not reacts:
        return

    for i, react in enumerate(reacts, 1):
        gravar_react(react, REACT_TIME, i)

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
