import os
import sys
import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
import pyautogui
from obsws_python import ReqClient
from moviepy import VideoFileClip

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../sultano")))

from editor.edit_videos import transform_horizontal_to_vertical

# ---------------- Configurações ----------------
REACT_TIME = 10
ARQUIVO_REACTS = "/Users/francisco/Downloads/reacts.txt"
FONTE_TITULO = "ReactTitle"
FONTE_TIMER = "ReactTimer"
DIRETORIO_GRAVACAO = "/Users/francisco/Movies"
INSTAGRAM_COLABS = ["@colab1", "@colab2"]

# OBS
client = ReqClient(host="localhost", port=4455, password="123123")

# Thread pool para conversão de vídeos
executor = ThreadPoolExecutor(max_workers=2)

# ---------------- Funções ----------------
def sanitizar_nome(nome):
    nome = re.sub(r'[<>:"/\\|?*]', '', nome)
    nome = nome.replace(' ', '_').replace('.', '_')
    return nome[:40]

def abrir_navegador_metade(lado="esquerda"):
    screen_width, screen_height = pyautogui.size()
    driver = webdriver.Chrome()
    
    if lado == "esquerda":
        x, width = 0, screen_width // 2
    else:  # direita
        x, width = screen_width // 2, screen_width // 2

    driver.set_window_rect(x=x, y=0, width=width, height=screen_height)
    return driver

def ler_reacts():
    with open(ARQUIVO_REACTS, 'r', encoding='utf-8') as f:
        reacts = [linha.strip() for linha in f if linha.strip()]
    print(f"✅ {len(reacts)} reacts carregados")
    return reacts

def configurar_titulo(texto):
    try:
        client.set_input_settings(FONTE_TITULO, {"text": texto}, overlay=True)
        print(f"📝 {texto}")
    except: pass

def atualizar_timer(segundos):
    try:
        texto = f"{segundos//60:02d}:{segundos%60:02d}"
        client.set_input_settings(FONTE_TIMER, {"text": texto}, overlay=True)
    except: pass

def format_instagram_for_filename(titulo):
    """
    Recebe o título ou username do Instagram e retorna no formato para arquivo:
    'instagram - username'
    """
    username = titulo.replace("https://www.instagram.com/", "").replace("/", "").strip()
    return f"instagram - {username}"

def gravar_react(titulo, tempo_total, idx):
    """Grava React e renomeia para 16x9"""
    try:
        configurar_titulo(titulo)
        time.sleep(0.5)

        # Formata título para o nome do arquivo
        titulo_formatado = format_instagram_for_filename(titulo)
        video_nome = os.path.join(
            DIRETORIO_GRAVACAO,
            f"{datetime.now():%Y-%m-%d %H-%M-%S} - {titulo_formatado} - React_{idx}-16x9.mp4"
        )
        
        # Para gravação existente
        try:
            status = client.get_record_status()
            if status.output_active:
                client.stop_record()
                time.sleep(2)
        except:
            pass
        
        print(f"⏺️  Iniciando gravação...")
        client.start_record()
        
        for s in range(tempo_total, 0, -1):
            atualizar_timer(s)
            time.sleep(1)
        
        client.stop_record()
        print(f"✅ Gravação finalizada: {video_nome}")
        
        # Renomeia arquivo real gerado
        arquivos = sorted(
            [f for f in os.listdir(DIRETORIO_GRAVACAO) if f.endswith(".mp4")],
            key=lambda x: os.path.getmtime(os.path.join(DIRETORIO_GRAVACAO, x))
        )
        ultimo = arquivos[-1]
        novo_path = os.path.join(DIRETORIO_GRAVACAO, os.path.basename(video_nome))
        os.rename(os.path.join(DIRETORIO_GRAVACAO, ultimo), novo_path)
        print(f"📁 Renomeado 16x9: {ultimo} -> {os.path.basename(video_nome)}")
        return novo_path
    except Exception as e:
        print(f"❌ Erro na gravação: {e}")
        return None

def converter_para_vertical_async(video_16x9):
    """Executa conversão para 9x16 em background"""
    def tarefa():
        clip = VideoFileClip(video_16x9)
        clip_vert = transform_horizontal_to_vertical(clip)
        base, ext = os.path.splitext(video_16x9)
        nome_vert = f"{base[:-4]}9x16{ext}"  # remove -16x9 e adiciona -9x16
        clip_vert.write_videofile(nome_vert, codec="libx264", audio_codec="aac")
        print(f"✅ Conversão vertical finalizada: {nome_vert}")
        # Aqui você pode chamar função de publicar no Instagram
    executor.submit(tarefa)

def abrir_link_instagram(driver, link):
    try:
        driver.get(link)
        time.sleep(2)  # espera carregar
    except Exception as e:
        print(f"❌ Erro ao abrir link: {e}")

# ---------------- Main ----------------
# ---------------- Main ----------------
def main():
    print("🚀 INICIANDO GRAVAÇÃO DE REACTS COM TRANSFORMAÇÃO VERTICAL")
    reacts = ler_reacts()
    if not reacts: 
        return
    
    driver = abrir_navegador_metade(lado="esquerda")
    
    videos_16x9 = []  # lista para armazenar caminhos dos vídeos
    
    for i, react in enumerate(reacts, 1):
        print(f"\n🎬 REACT {i}: {react}")
        def format_instagram_url(username):
            username = username.replace("https://www.instagram.com/", "").strip("/")
            return f"https://www.instagram.com/{username}/"
        
        abrir_link_instagram(driver, format_instagram_url(react))
        
        video_16x9 = gravar_react(react, REACT_TIME, i)
        if video_16x9:
            videos_16x9.append(video_16x9)
        
        print("🗑️ Pronto para próximo react")
    
    driver.quit()
    print("🎉 TODOS REACTS PROCESSADOS!")

    # ---------------- Converter todos depois ----------------
    print("🚀 INICIANDO CONVERSÃO PARA VERTICAL (9x16)")
    for video_16x9 in videos_16x9:
        clip = VideoFileClip(video_16x9)
        clip_vert = transform_horizontal_to_vertical(clip)
        base, ext = os.path.splitext(video_16x9)
        nome_vert = f"{base[:-4]}9x16{ext}"  # remove -16x9 e adiciona -9x16
        clip_vert.write_videofile(nome_vert, codec="libx264", audio_codec="aac")
        print(f"✅ Conversão vertical finalizada: {nome_vert}")

if __name__ == "__main__":
    main()
