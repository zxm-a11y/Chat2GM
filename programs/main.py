from flask import Flask, render_template, request, jsonify
import os
# 文件上传
from werkzeug.utils import secure_filename
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
from models import db, Chat, ChatHistory
from datetime import datetime, timedelta
# 导入加载工具的库 使用initialize_agent初始化agent 配置搜索工具
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
# 配置日志
import logging
from logging.handlers import RotatingFileHandler
# 配置日志记录
logging.basicConfig(level=logging.INFO)
# 创建一个日志处理器，用于写入日志文件
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024, backupCount=10)
file_handler.setLevel(logging.INFO)
# 创建一个日志格式器并添加到处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logging.getLogger('').addHandler(file_handler)
# 设置OpenAI API Key
os.environ["OPENAI_API_KEY"] = "YOUR OPENAI_API_KEY"
# 搜索的密钥
os.environ["SERPAPI_API_KEY"] = "YOUR SERPAPI_API_KEY"
# 配置大模型
llm = ChatOpenAI(temperature=0.0, model="gpt-4")
# 加载工具 配置serpapi搜索工具
llms = OpenAI(temperature=0,model_name="gpt-3.5-turbo")
tools = load_tools(["serpapi"])

app = Flask(__name__)
# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
# 定义csv_file_path为全局变量  为将上传的文件传入到agent中
csv_file_path = None
@app.route("/")
def index():
    # 将聊天记录按照时间
    chats = Chat.query.order_by(Chat.start_time.desc()).all()
    chat_histories = {
        "today": [],
        "yesterday": [],
        "older": [],
        "flag":False
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
# 上传文件
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('./', filename)
        file.save(filepath)
        # 文件路径存储
        global csv_file_path
        csv_file_path = filepath
        logging.info("CSV file '%s' uploaded successfully", filename)
        return jsonify({"status": "success", "flag":True,"message": "orginal file has been uploaded"}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400
# 发送消息
@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    logging.info("Received message: %s", message)
    print("接收到的消息:", message)
    # 根据是否上传了文件进行判断 如果上传了文件就是用langchain create_csv_agent
    if csv_file_path:
        answer = chat_with_csv_agent(message)
    else:
        # 进行对话 问关于细菌的问题会使用配置的搜索工具
        answer = chat_google(message)
    new_chat = Chat()
    db.session.add(new_chat)
    db.session.flush()
    chat_id = new_chat.id
    chat_record = ChatHistory(chat_id=chat_id,message=message, response=str(answer))
    db.session.add(chat_record)
    db.session.commit()
    return jsonify({"status": "success", "answer": str(answer)})
# langchain聊天
# 上传文件之后 文件数据分析使用的是create_csv_agent
def chat_with_csv_agent(q):
    agent = create_csv_agent(llm, csv_file_path, verbose=True)
    return agent.run(q)
# 没有上传文件，直接对话使用的是 用initialize_agent初始化后的agent 配置了搜索的功能
def chat_google(q):
    agents = initialize_agent(tools, llms, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    return agents.run(q)
if __name__ == '__main__':
    app.run()
