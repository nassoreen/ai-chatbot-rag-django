
<h1 align="center">AI Chatbot with RAG (Django + Ollama)</h1>

### DEMO
 ![](https://github.com/nassoreen/chatbot/blob/main/images/demo.png)
 
An AI-powered chatbot system using Retrieval-Augmented Generation (RAG) to provide accurate answers based on an organization’s knowledge base. This approach improves reliability and reduces hallucinations from AI models.



### Features
- Automatic AI chatbot for answering questions
- Knowledge retrieval using vector similarity search
- LLM integration via Ollama
- Admin panel for managing knowledge base
- Chat history tracking
- Supports contextual and continuous conversations


### Tech Stack
- Backend: Django
- Database: PostgreSQL
- AI Model: Ollama (LLM)
- Embedding: SentenceTransformers
- Search: Vector Similarity Search

### How It Works (RAG)
![](https://github.com/nassoreen/chatbot/blob/main/images/RAG.png)



## Installation


1. Clone Repository

```sh
git clone https://github.com/nassoreen/chatbot.git
```
```sh
cd chatbot
```


2. Create Virtual Environment

```sh
python -m venv venv
```
```sh
source venv/bin/activate   # Windows: venv\Scripts\activate
```


3. Install Dependencies

```sh
pip install -r requirements.txt
```


4. Setup Database

```sh
python manage.py migrate
```


5. Run Ollama (LLM)

```sh
ollama run llama3
```


6. Run Server
   
```sh
python manage.py runserver
```



### Limitations

- Requires a prepared knowledge base
- Performance depends on data quality
- LLM requires sufficient system resources
