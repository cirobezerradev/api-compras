"""Tela de interação do Agente de Compras da Manutenção.

Rodar: streamlit run app.py
"""

import openai
import streamlit as st

from agente import INSTRUCOES, MODELO, TOOLS, rodar_agente

st.set_page_config(page_title="Agente de Compras da Manutenção", page_icon="🛒")
st.title("🛒 Agente de Compras da Manutenção")
st.caption(f"Modelo: {MODELO}")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = [{"role": "system", "content": INSTRUCOES}]
    st.session_state.tokens = 0

with st.sidebar:
    st.subheader("Ferramentas do agente")
    for t in TOOLS:
        st.markdown(f"**{t['function']['name']}**  \n{t['function']['description']}")
    st.divider()
    painel = st.container()
    if st.button("Nova conversa"):
        st.session_state.mensagens = [{"role": "system", "content": INSTRUCOES}]
        st.session_state.tokens = 0
        st.rerun()

for m in st.session_state.mensagens[1:]:
    if m["role"] in ("user", "assistant") and m.get("content"):
        st.chat_message(m["role"]).write(m["content"])

if pergunta := st.chat_input("Pergunte sobre fornecedor, preço ou data de parada"):
    st.chat_message("user").write(pergunta)
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("assistant"):
        try:
            with st.spinner("O agente está consultando..."):
                resposta, usadas, tokens = rodar_agente(st.session_state.mensagens)
            st.session_state.tokens += tokens
            st.write(resposta)
            # ---------- Etapa 5: mostrar as ferramentas usadas ----------
            if usadas:
                with st.expander(f"Ferramentas usadas ({len(usadas)})"):
                    for nome, args, resultado in usadas:
                        st.markdown(f"**{nome}** `{args}`")
                        st.json(resultado)
        except openai.AuthenticationError:
            st.error("Chave da API inválida. Confira o .env e reinicie o app.")
        except openai.APIConnectionError:
            st.error("Sem conexão com a API. Confira a internet.")
        except openai.OpenAIError as erro:
            st.error(f"Erro na chamada: {erro}")

with painel:
    st.metric("Tokens usados nesta conversa", st.session_state.tokens)
