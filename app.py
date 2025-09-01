import streamlit as st
import pandas as pd
import random
import unicodedata

# --- Função para remover acentos ---
def normalizar(texto):
    if pd.isna(texto):
        return ""
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8").lower()

# --- Carregar DataFrame (exemplo) ---
@st.cache_data
def carregar_dados():
    return pd.read_csv("artilheiros.csv")  # colunas: jogador, gols

df = carregar_dados()

# --- Inicialização do jogo ---
if "letra" not in st.session_state:
    st.session_state.letra = None
if "df_top5" not in st.session_state:
    st.session_state.df_top5 = None
if "jogo" not in st.session_state:
    st.session_state.jogo = None
if "tentativas" not in st.session_state:
    st.session_state.tentativas = 0

st.title("⚽ Desafio dos Artilheiros")

# --- Escolher ou sortear letra ---
col1, col2 = st.columns(2)
with col1:
    letra_escolhida = st.text_input("Digite uma letra (A-Z):").upper().strip()
with col2:
    if st.button("🎲 Sortear letra"):
        st.session_state.letra = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        letra_escolhida = st.session_state.letra

# Se o usuário digitou uma letra válida, define a letra do jogo
if letra_escolhida and letra_escolhida in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    if st.session_state.letra != letra_escolhida:
        # Reinicia o jogo com a nova letra
        st.session_state.letra = letra_escolhida
        df_letra = df[df["jogador"].str.startswith(st.session_state.letra, na=False)]
        df_top5 = df_letra.sort_values(by="gols", ascending=False).head(5).reset_index(drop=True)
        st.session_state.df_top5 = df_top5
        st.session_state.jogo = ["____________" for _ in range(len(df_top5))]
        st.session_state.tentativas = 0

# Só continua se já temos uma letra definida
if st.session_state.df_top5 is not None and not st.session_state.df_top5.empty:
    st.write(f"🔤 **Letra atual:** {st.session_state.letra}")

    # Mostra tabela parcial
    for i, (nome, gols) in enumerate(zip(st.session_state.jogo, st.session_state.df_top5["gols"]), start=1):
        st.write(f"{i}º {nome} ({gols} gols)")

    # Campo para chute
    chute = st.text_input("Digite o nome de um jogador:")

    if st.button("Chutar"):
        st.session_state.tentativas += 1
        chute_norm = normalizar(chute)

        acertou = False
        for i, jogador in enumerate(st.session_state.df_top5["jogador"]):
            if st.session_state.jogo[i] != "____________":
                continue
            partes_nome = [normalizar(p) for p in jogador.split()]
            if chute_norm in partes_nome or chute_norm == normalizar(jogador):
                st.session_state.jogo[i] = jogador  # 👉 agora atualiza
                acertou = True
                st.success(f"✅ Acertou! {jogador} revelado.")
                st.experimental_rerun()  # força atualização da tela
                break
        if not acertou:
            st.error("❌ Errou ou já estava revelado!")

    # Verifica se terminou
    if "____________" not in st.session_state.jogo:
        st.subheader("🏆 Resultado Final")
        for i, (nome, gols) in enumerate(zip(st.session_state.df_top5["jogador"], st.session_state.df_top5["gols"]), start=1):
            st.write(f"{i}º {nome} ({gols} gols)")
        st.write(f"🔢 Você precisou de **{st.session_state.tentativas} tentativas**!")

        if st.button("🔄 Jogar novamente"):
            for key in ["letra", "df_top5", "jogo", "tentativas"]:
                st.session_state.pop(key)
            st.experimental_rerun()
