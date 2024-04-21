# Chat2GM
## Introduce
Chat2GM - a LLM module has been developed especially for **gut microbiota** data analysis using **the LangChain framework** and **API of the OpenAI GPT model**. <br>The module comprises webpage templates and back-end python service using **Python Flask framework**. The webpage allows users to upload data and input prompts, and it has an aesthetic interface design and clear layouts. 
#### The layout and function of Chat2GM user interface
* Left part is for starting a new chat and listing the chat history.
* Question-Answer pairs are shown in the middle zone.
* An input box is set for giving instructions or prompts on the bottom of the middle part.
* On the right side,the file-upload button is for uploading data in Excel format; some simple charts could be shown for the analysis.
#### The Chat2GM user interface display
.<div align=center><img src="https://github.com/zxm-a11y/Chat2GM/assets/156500479/e4df0dd8-939a-484a-8e86-0b08e28858e1" /></div>
## Instruction
### 1.Prepare API
(1)The project uses the **OpenAI interface**. You need to go to [OpenAI Registration Page](https://beta.openai.com/signup "OpenAI Registration Page") to create an account, and then go to [API Management Page](https://beta.openai.com/account/API-keys "API Management Page") to create an API after creating the account. The interface requires overseas network access and binding credit card payment.
<br>
(2)Apply for **serper's key** in [serper.com](https://serper.dev/API-key "serper.com") in official website to configure the key to realize the search function in the project.
### 2.Operate environment
Windows system is supported, and Python needs to be installed. `Python 3.11.8` was used in the development of this project.
#### (1)Clone project code
```python  
git clone https://github.com/zxm-a11y/Chat2GM
cd Chat2GM/programs  
```
#### (2)Install core dependencies
```python
pip3 install -r requirements.txt
```
### 3.Configuration
Configure the api of **openai** and the key of **serper** in the `main.py` file.
### 4.Run locally
```python
python3 main.py
```

