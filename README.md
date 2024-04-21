# Chat2GM
## Introduce
Chat2GM - a LLM module has been developed especially for **gut microbiota** data analysis using **the LangChain framework** and **API of the OpenAI GPT model**. <br>The module is composed of webpage templates and back-end python service using **Python Flask framework**. The webpage is for users to upload data and input prompts, and it has an aesthetic interface design and clear layouts. 
#### The layout and function of Chat2GM user interface
* Left part is for starting a new chat and listing the chat history.
* Question-Answer pairs are shown in the middle zone.
* An input box is set for giving instruc-tions or prompts on the bottom of the middle part.
* On the right side,the file-upload button is for uploading data with Excel format, and some simple charts could be shown for the analysis.
#### The Chat2GM user interface display
.<div align=center><img src="https://github.com/zxm-a11y/Chat2GM/assets/156500479/e4df0dd8-939a-484a-8e86-0b08e28858e1" /></div>
## Instruction
### 1.API准备
(1)项目默认使用OpenAI接口，需前往[OpenAI注册页面](https://beta.openai.com/signup "OpenAI注册页面")创建账号，创建完账号则前往[API管理页面](https://beta.openai.com/account/api-keys,"API管理页面")创建一个API Key 并保存下来，后面需要在项目中配置这个key。接口需要海外网络访问及绑定信用卡支付。<br>
(2)在[serper.com](https://serper.dev/api-key,"serper.com")官网申请serper的key,用于配置在项目中实现搜索功能的key
### 2.运行环境
#### (1)克隆项目代码
```python  
git clone https://github.com/zxm-a11y/Chat2GM
cd Chat2GM/  
```
#### (2)安装核心依赖
```python
pip3 install -r requirements.txt
```
### 3.配置
配置openai的api和搜索的api
### 4.本地运行
```python
python3 main.py
```

