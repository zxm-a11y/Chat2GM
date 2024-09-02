import os
import logging
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from logging.handlers import RotatingFileHandler
from langchain_openai import ChatOpenAI
from models import db, Chat, ChatHistory
from langchain_experimental.agents import create_pandas_dataframe_agent

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage

# Environment variables for sensitive keys
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["SERPAPI_API_KEY"] = "944d35e4e36b87efc1e0eb3660604db2bc9a8060df3c8b96a789e9089e3fc88c"

# Configure logging
logging.basicConfig(level=logging.INFO)
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=10)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logging.getLogger('').addHandler(file_handler)

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# Global variable to store CSV file path
csv_file_path = None

# Initialize LLM
llm = ChatOpenAI(
    openai_api_base="https://www.apigptopen.xyz/v1",
    openai_api_key="sk-vowNrKrNfzCDjMfkC9D018E5A4Bc4f6891C96228991f39Ad",
    temperature=0
)

PDF = 'gut_microbiota.pdf'
loader = PyPDFLoader(PDF)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=OllamaEmbeddings(model="nomic-embed-text"))

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()

# Create retriever tool
tool = create_retriever_tool(
    retriever,
    "search_agents_answer",
    "Searches and returns context from LLM Powered Autonomous Agents. Answering questions about the gut microbiota.",
)
tools = [tool]

# Create REACT agent executor
agent_executor = create_react_agent(llm, tools)

@app.route("/")
def index():
    # Fetch chat history and categorize by date
    chats = Chat.query.order_by(Chat.start_time.desc()).all()
    chat_histories = {
        "today": [],
        "yesterday": [],
        "older": [],
        "flag": False
    }
    today = datetime.utcnow().date()
    for chat in chats:
        history = ChatHistory.query.filter_by(chat_id=chat.id).order_by(ChatHistory.timestamp.asc()).first()
        if history:
            if history.timestamp.date() == today:
                chat_histories["today"].append((chat.id, history))
            elif history.timestamp.date() == today - timedelta(days=1):
                chat_histories["yesterday"].append((chat.id, history))
            else:
                chat_histories["older"].append((chat.id, history))

    logging.info("Rendering index page with %d chat records", len(chats))
    return render_template('index.html', chat_histories=chat_histories)


# File upload endpoint
@app.route('/upload_file', methods=['POST'])
def upload_file():
    global csv_file_path
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('./', filename)
        file.save(filepath)
        csv_file_path = filepath
        logging.info("CSV file '%s' uploaded successfully", filename)
        return jsonify({"status": "success", "flag": True, "message": "Original file has been uploaded"}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400


# Send message endpoint
@app.route('/send_message', methods=['POST'])
def send_message():
    global csv_file_path
    message = request.form['message']
    logging.info("Received message: %s", message)

    # Handle message with appropriate agent
    if csv_file_path:
        df = pd.read_csv(csv_file_path)
        answer = chat_with_csv_agent(message, df)
    else:
        answer = chat_google(message)

    # Create chat and history records
    new_chat = Chat(start_time=datetime.utcnow())
    db.session.add(new_chat)
    db.session.flush()
    chat_id = new_chat.id

    chat_record = ChatHistory(chat_id=chat_id, message=message, response=str(answer))
    db.session.add(chat_record)
    db.session.commit()

    return jsonify({"status": "success", "answer": str(answer)})


# Chat with CSV agent
def chat_with_csv_agent(q, df):
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        agent_type="tool-calling",
        verbose=True,
        allow_dangerous_code=True
    )
    return agent.invoke(q)


# Chat with Google and retriever tools
def chat_google(q):
    meg = agent_executor.invoke({"messages": [HumanMessage(content=q)]})
    return meg['messages'][3].content


if __name__ == '__main__':
    # Avoid double loading in debug mode
    app.run(debug=True, use_reloader=False)
