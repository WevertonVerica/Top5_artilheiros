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
# Substitua pelo seu arquivo final
@st.cache_data
def carregar_dados():
    return pd.read_csv("artilheiros.csv")  # tem colunas: jogador, gols

df = carregar_dados()

# --- Inicialização do jogo ---
if "letra" not in st.session_state:
    st.session_state.letra = random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    df_letra = df[df["jogador"].str.startswith(st.session_state.letra, na=False)]
    df_top5 = df_letra.sort_values(by="gols", ascending=False).head(5).reset_index(drop=True)

    st.session_state.df_top5 = df_top5
    st.session_state.jogo = ["____________" for _ in range(len(df_top5))]
    st.session_state.tentativas = 0

st.title("⚽ Desafio dos Artilheiros")
st.write(f"🔤 **Letra sorteada:** {st.session_state.letra}")

# Mostra a tabela parcial
for i, (nome, gols) in enumerate(zip(st.session_state.jogo, st.session_state.df_top5["gols"]), start=1):
    st.write(f"{i}º {nome} ({gols} gols)")

# Input do jogador
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
            st.session_state.jogo[i] = jogador
            acertou = True
            st.success(f"✅ Acertou! {jogador} revelado.")
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