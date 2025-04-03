    import streamlit as st
import pandas as pd
from io import BytesIO
import json
from xlsxwriter import Workbook

# Carregamento do arquivo JSON
with open('Lojas.json', 'rb') as f:
    data = json.load(f)
    lojas = data.get("Lojas", {})
    produtos = data.get("Produtos", {})

# Gerenciamento do estado de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login Frosty")
    username = st.selectbox("Selecione o usuário:", list(lojas.keys()))
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if username in lojas and lojas[username]["Senha"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.loja_usuario = username.split('___')[0]  
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")
else:
    st.title("Saídas a granel")
    
    if "registros" not in st.session_state:
        st.session_state.registros = pd.DataFrame(columns=["Código do Produto", "Produto", "Quantidade", "Depósito", "Centro de Custo", "Loja"])
    
    st.title("Registro de Consumo de Produtos")
    
    produto_selecionado = st.selectbox("Selecione o produto:", list(produtos.keys()))
    quantidade = st.number_input("Quantidade consumida:", min_value=1, step=1)
    
    if st.button("Registrar Consumo"):
        if quantidade == 0 or quantidade > 100:
            st.error("Por favor, preencha o campo com um valor válido (entre 1 e 100).")
        else:
            loja_selecionada = st.session_state.loja_usuario
            novo_registro = pd.DataFrame.from_records([
                {
                    "Loja": loja_selecionada,
                    "Centro de Custo": lojas[loja_selecionada]["centro_custo"],
                    "Depósito": lojas[loja_selecionada]["deposito"],
                    "Código do Produto": produto_selecionado,
                    "Produto": produtos[produto_selecionado],
                    "Quantidade": quantidade
                }
            ])
            st.session_state.registros = pd.concat([st.session_state.registros, novo_registro], ignore_index=True)
            st.success("Registro adicionado com sucesso!")
    
    st.subheader("Registros de Consumo")
    
    if not st.session_state.registros.empty:
        for i, row in st.session_state.registros.iterrows():
            col1, col2 = st.columns([0.9, 0.1])  
            with col1:
                st.write(f"**Loja:** {row['Loja']} | **Produto:** {row['Produto']} | **Quantidade:** {row['Quantidade']}")
            with col2:
                if st.button("❌", key=f"delete_{i}"):
                    st.session_state.registros = st.session_state.registros.drop(i).reset_index(drop=True)
                    st.rerun()
    
    # Correção do botão de download do Excel
    if not st.session_state.registros.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            st.session_state.registros.to_excel(writer, index=False, sheet_name='Resultados Lojas')
        
        output.seek(0)
        st.download_button(
            label="Baixar Registros em Excel",
            data=output,
            file_name="registros_consumo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    if st.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

def fim ():
    Print 
