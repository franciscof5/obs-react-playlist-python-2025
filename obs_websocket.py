import time
import os
from obsws_python import ReqClient

# Configurações
REACT_TIME = 10
ARQUIVO_REACTS = "/Users/francisco/Downloads/reacts.txt"
FONTE_TITULO = "ReactTitle"
FONTE_TIMER = "ReactTimer"

# Configuração do cliente OBS
client = ReqClient(host="localhost", port=4455, password="123123")

def ler_reacts(arquivo):
    """Lê o arquivo de reacts e retorna uma lista"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            reacts = [linha.strip() for linha in f if linha.strip()]
        return reacts
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo} não encontrado!")
        return []
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []

def configurar_titulo(texto):
    """Configura o texto do título"""
    try:
        settings = {
            "text": texto,
            "font": {
                "face": "Arial Black",
                "size": 56,
                "style": "Bold",
                "flags": 1
            },
            "color": 16777215,  # Branco
            "align": "center"
        }
        client.set_input_settings(FONTE_TITULO, settings, overlay=True)
        print(f"📝 Título definido: {texto}")
    except Exception as e:
        print(f"❌ Erro ao configurar título: {e}")

def atualizar_timer(segundos_restantes):
    """Atualiza o timer com o tempo restante"""
    try:
        minutos = segundos_restantes // 60
        segundos = segundos_restantes % 60
        texto_timer = f"{minutos:02d}:{segundos:02d}"
        
        settings = {
            "text": texto_timer,
            "font": {
                "face": "Consolas",
                "size": 42,
                "style": "Bold",
                "flags": 1
            },
            "color": 65280 if segundos_restantes > 10 else 16711680,  # Verde ou Vermelho
            "align": "center"
        }
        client.set_input_settings(FONTE_TIMER, settings, overlay=True)
    except Exception as e:
        print(f"❌ Erro ao atualizar timer: {e}")

def gravar_react(titulo, tempo_total):
    """Grava um react individual"""
    try:
        # Configurar título
        configurar_titulo(titulo)
        time.sleep(1)  # Pequena pausa para garantir atualização
        
        # Verificar se já está gravando
        status = client.get_record_status()
        if status.output_active:
            client.stop_record()
            time.sleep(2)
        
        # Iniciar gravação
        print(f"🎥 Iniciando gravação de {tempo_total}s: {titulo}")
        client.start_record()
        
        # Loop do timer
        for segundos_restantes in range(tempo_total, 0, -1):
            atualizar_timer(segundos_restantes)
            time.sleep(1)
            
            # Feedback a cada 10 segundos
            if segundos_restantes % 10 == 0:
                print(f"⏰ {segundos_restantes}s restantes: {titulo}")
        
        # Finalizar gravação
        client.stop_record()
        print(f"✅ Gravação finalizada: {titulo}")
        time.sleep(2)  # Pausa entre gravações
        
    except Exception as e:
        print(f"❌ Erro durante gravação: {e}")

def main():
    """Função principal"""
    print("🎬 Iniciando produção de reacts...")
    
    # Ler reacts do arquivo
    reacts = ler_reacts(ARQUIVO_REACTS)
    
    if not reacts:
        print("Nenhum react encontrado para gravar!")
        return
    
    print(f"📋 Reacts encontrados: {len(reacts)}")
    for i, react in enumerate(reacts, 1):
        print(f"  {i}. {react}")
    
    print(f"\n⏰ Tempo por react: {REACT_TIME} segundos")
    print("=" * 50)
    
    # Gravar cada react
    for i, react in enumerate(reacts, 1):
        print(f"\n🎬 React {i}/{len(reacts)}")
        gravar_react(react, REACT_TIME)
    
    print("\n" + "=" * 50)
    print("🎉 Produção de reacts concluída!")
    print(f"📊 Total de vídeos gravados: {len(reacts)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Script interrompido pelo usuário")
        try:
            client.stop_record()
        except:
            pass
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
    finally:
        try:
            client.disconnect()
        except:
            pass