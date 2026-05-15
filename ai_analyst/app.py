import os
from pathlib import Path

import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Настройка страницы ---
st.set_page_config(page_title="Local AI Analyst", layout="wide")
st.title("🤖 Локальный ИИ-Аналитик")


@st.cache_resource
def init_ai():
    """Инициализирует LLM и векторную БД (кэшируется между перезапусками UI)."""
    db_path = "./vector_db_ui"
    embeddings = OllamaEmbeddings(model="llama3")
    llm = ChatOllama(model="llama3", temperature=0.2, num_ctx=8192)
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return llm, vector_db


llm, vector_db = init_ai()


with st.sidebar:
    st.header("🗂 Загрузка документов")
    uploaded_files = st.file_uploader(
        "Выберите файлы Word или PDF",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )

    if st.button("Проанализировать и обучиться"):
        if uploaded_files:
            with st.spinner("Изучаю документы..."):
                for uploaded_file in uploaded_files:
                    temp_path = Path(f"./temp_{uploaded_file.name}")
                    temp_path.write_bytes(uploaded_file.getbuffer())

                    try:
                        if uploaded_file.name.lower().endswith(".pdf"):
                            loader = PyPDFLoader(str(temp_path))
                        else:
                            loader = Docx2txtLoader(str(temp_path))

                        docs = loader.load()
                        for d in docs:
                            d.metadata["filename"] = uploaded_file.name

                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000,
                            chunk_overlap=200,
                        )
                        chunks = splitter.split_documents(docs)
                        vector_db.add_documents(chunks)
                    finally:
                        if temp_path.exists():
                            os.remove(temp_path)

            st.success("База знаний обновлена!")
        else:
            st.warning("Сначала выберите файлы.")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Задайте вопрос по вашим документам..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Анализирую источники..."):
            system_style = (
                "Вы — эксперт-аналитик. Дайте точный ответ на основе документов.\n"
                "ОБЯЗАТЕЛЬНО ссылайтесь на название документа и его детали в тексте ответа.\n"
                "В конце добавьте раздел '🔍 РЕКОМЕНДУЕМЫЕ ВОПРОСЫ' с 3 пунктами.\n\n"
                "КОНТЕКСТ:\n{context}"
            )

            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_style), ("human", "{input}")]
            )

            retriever = vector_db.as_retriever(search_kwargs={"k": 7})
            combine_docs_chain = create_stuff_documents_chain(llm, prompt_template)
            rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

            response = rag_chain.invoke({"input": prompt})
            full_response = response["answer"]

            sources = list(
                {
                    os.path.basename(doc.metadata.get("filename", "Unknown"))
                    for doc in response["context"]
                }
            )
            if sources:
                full_response += (
                    "\n\n---\n**Использованные источники:** " + ", ".join(sources)
                )

            st.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
