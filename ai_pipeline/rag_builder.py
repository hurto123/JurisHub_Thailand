import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
TXT_INBOX = os.path.join(DATA_DIR, "01_raw_text")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "database", "chroma_db")

OLLAMA_MODEL = "deepseek-r1:1.5b"
EMBEDDING_MODEL = "nomic-embed-text" # Small embedder recommended for Ollama

def build_law_rag():
    print("⚖️ Initializing deepseek_LAW RAG System...")
    
    # 1. Load Legal Texts
    txt_files = glob.glob(os.path.join(TXT_INBOX, "*.txt"))
    if not txt_files:
        print("⚠️ No law text files found in 01_raw_text to build the knowledge base.")
        return None

    print(f"📄 Found {len(txt_files)} legal documents.")
    docs = []
    for file in txt_files:
        try:
            loader = TextLoader(file, encoding='utf-8')
            docs.extend(loader.load())
        except Exception as e:
            print(f"Skipping {file} due to encoding error: {e}")

    # 2. Split into chunks to build Vector DB
    print("🔪 Chunking legal documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    # 3. Create or Load Vector Database
    print("🧠 Building Vector Database (ChromaDB)... This may take some time.")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    # vectorstore.persist() is automatic in newer versions
    
    # 4. Setup Retrieval QA Chain (DeepSeek_LAW)
    print(f"🤖 Initializing {OLLAMA_MODEL} as deepseek_LAW...")
    llm = Ollama(model=OLLAMA_MODEL, temperature=0.1)
    
    prompt_template = """คุณคือ "DeepSeek_LAW" ปัญญาประดิษฐ์นักกฎหมายไทยผู้เชี่ยวชาญ
ใช้ข้อมูลบริบท (Context) ที่ให้มาเพื่อตอบคำถามเกี่ยวกับกฎหมายเท่านั้น 
หากข้อมูลในบริบทไม่เพียงพอต่อการตอบคำถาม ให้บอกไปตรงๆ ว่าไม่มีข้อมูลในคลังกฎหมาย ห้ามคิดเดาข้อกฎหมายเองเด็ดขาด

Context (ข้อมูลข้อกฎหมาย):
{context}

คำถามจากผู้ใช้: {question}

คำตอบของ DeepSeek_LAW:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    print("✅ deepseek_LAW RAG System is Ready!")
    return qa_chain

def chat_interface():
    qa_chain = build_law_rag()
    if not qa_chain:
        return
        
    print("\n=============================================")
    print("💬 Welcome to deepseek_LAW Interactive Shell")
    print("Type 'exit' or 'quit' to close.")
    print("=============================================\n")
    
    while True:
        query = input("🧑‍🎓 คำถามกฎหมาย: ")
        if query.lower() in ['exit', 'quit']:
            break
            
        print("⚖️ deepseek_LAW กำลังค้นหามาตราและวิเคราะห์...")
        try:
            result = qa_chain({"query": query})
            print(f"\n🤖 ตอบ:\n{result['result']}")
            
            print("\n📌 อ้างอิงจากคลังข้อมูล:")
            for i, doc in enumerate(result['source_documents'], 1):
                source = os.path.basename(doc.metadata.get('source', 'Unknown'))
                print(f"[{i}] {source}")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error during generation: {e}")

if __name__ == "__main__":
    chat_interface()
