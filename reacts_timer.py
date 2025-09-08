import obspython as obs
import time

# ==============================
# CONFIGURAÇÕES
# ==============================
REACT_TIME = 60  # tempo de cada react em segundos (use 300 para 5 min)
ARQUIVO_LISTA = "C:/Users/SeuUsuario/reacts.txt"  # ajuste o caminho do arquivo
FONTE_TITULO = "ReactTitle"   # nome da fonte de texto para título
FONTE_TIMER = "ReactTimer"    # nome da fonte de texto para cronômetro
# ==============================

titulos = []
indice_atual = 0
ultimo_tempo = 0


# Carregar lista de reacts do arquivo
def carregar_lista():
    global titulos
    try:
        with open(ARQUIVO_LISTA, "r", encoding="utf-8") as f:
            titulos = [linha.strip() for linha in f if linha.strip()]
    except Exception as e:
        print("Erro ao carregar lista:", e)
        titulos = []


# Atualizar texto da fonte no OBS
def atualizar_fonte(nome_fonte, texto):
    fonte = obs.obs_get_source_by_name(nome_fonte)
    if fonte is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", texto)
        obs.obs_source_update(fonte, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(fonte)


# Mudar para o próximo título
def atualizar_titulo():
    global indice_atual
    if not titulos:
        return
    atualizar_fonte(FONTE_TITULO, titulos[indice_atual])
    print(f"[OBS] Mudando título para: {titulos[indice_atual]}")
    indice_atual = (indice_atual + 1) % len(titulos)


# Atualizar cronômetro
def atualizar_timer(segundos_restantes):
    minutos = segundos_restantes // 60
    segundos = segundos_restantes % 60
    texto = f"{minutos:02d}:{segundos:02d}"
    atualizar_fonte(FONTE_TIMER, texto)


# Tick chamado a cada segundo
def tick():
    global ultimo_tempo
    agora = time.time()
    elapsed = int(agora - ultimo_tempo)
    restante = REACT_TIME - elapsed

    if restante >= 0:
        atualizar_timer(restante)

    if restante <= 0:  # tempo acabou
        ultimo_tempo = agora
        atualizar_titulo()
        # reinicia gravação
        obs.obs_frontend_recording_stop()
        obs.timer_add(iniciar_gravacao, 1000)


def iniciar_gravacao():
    obs.obs_frontend_recording_start()
    obs.timer_remove(iniciar_gravacao)


# OBS API
def script_description():
    return ("Alterna textos de reacts automaticamente a cada REACT_TIME.\n"
            "Mostra cronômetro regressivo na fonte 'ReactTimer'.\n"
            "Precisa de duas fontes de texto no OBS: 'ReactTitle' e 'ReactTimer'.")


def script_load(settings):
    global ultimo_tempo
    carregar_lista()
    ultimo_tempo = time.time()
    atualizar_titulo()
    atualizar_timer(REACT_TIME)
    obs.timer_add(tick, 1000)


def script_unload():
    obs.timer_remove(tick)
