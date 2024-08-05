# Cohere QA Flask Application

This project is a Flask web application that processes a document, stores its chunks in ChromaDB, and uses Cohere's language model to answer user questions. The answers are generated in the question's language and enhanced with relevant emojis.

## Features

- Read and process a DOCX document.
- Store document chunks in ChromaDB with embeddings.
- Answer user questions using the most relevant document chunk.
- Append relevant emojis to the answers.

## Setup

### Prerequisites

- Python 3.8 or higher
- A Cohere API key
- `pip` for installing dependencies

### Installation

1. Clone the repository.

2. Create and activate a virtual environment (optional but recommended).

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Packages

The `requirements.txt` file includes the following packages:

- `chromadb==0.5.5`
- `cohere==5.6.2`
- `emoji==2.12.1`
- `Flask==3.0.3`
- `langchain==0.2.11`
- `python_docx==1.1.2`

4. Add your Cohere API key in `app.py`:

   ```python
   cohere_api_key = 'your_cohere_api_key_here'
   ```

### Running with Docker

1. Build the Docker image:

   ```bash
   docker build -t flask-cohere-app .
   ```

2. Run the Docker container:

   ```bash
   docker run -p 5000:5000 flask-cohere-app
   ```

## Usage

1. Place your DOCX document in the project directory and update the `file_path` variable in `app.py` with your document's filename.

2. Run the Flask application:

   ```bash
   python3 app.py
   ```

3. Send a POST request to the `/ask` endpoint with the user's name and question:

   ```json
   {
     "user_name": "Usuario 1",
     "question": "¿Quién es Zara?"
   }
   ```

4. Receive a JSON response with the answer and relevant emojis:

   ```json
   {
     "user_name": "Usuario 1",
     "question": "¿Quién es Zara?",
     "answer": "Zara es un intrépido explorador con el que enfrentarse a desafíos cósmicos y viajar por planetas hostiles en busca de la paz en la distante galaxia de Zenthoria. 🌌🪐"
   }
   ```

## Additional Files

- **Dockerfile**: Contains the instructions to build the Docker image.
- **RAG_API.postman_collection.json**: Example Postman collection for testing the API.
- **report.ipynb**: Jupyter notebook with a summary of the challenge and some of the tests performed.

## Prompts for Cohere API

### Prompt for Generating Answer
The following prompt is used to generate answers based on the document context and user question:

```
Contexto: {most_relevant_chunk}
Pregunta: {user_question}
Responde en español y en tercera persona en una oración.
```

### Prompt for Generating Emojis
The following prompt is used to generate emojis that represent the answer:

```
Answer: {first_sentence}
Add two or three emojis that represent this answer:
```

### Example Usage in Code

Here is how the prompts are used in the `app.py` script:

```python
# Prompt for generating the answer
prompt = f"Contexto: {most_relevant_chunk}\nPregunta: {user_question}\nResponde en español y en tercera persona en una oración."

# Generate the answer using Cohere
response = co.generate(prompt=prompt, model='command', max_tokens=150)
generated_answer = response.generations[0].text.strip()

# Extract the first sentence of the generated answer
first_sentence = generated_answer.split('.')[0] + '.'

# Prompt for generating emojis
emoji_prompt = f"Answer: {first_sentence}\nAdd two or three emojis that represent this answer:"

# Generate emojis using Cohere
emoji_response = co.generate(prompt=emoji_prompt, model='command', max_tokens=10)
emoji_text = emoji_response.generations[0].text.strip()

# Filter to keep only emojis
emojis = ''.join([char for char in emoji_text if emoji.is_emoji(char)])

# Append emojis to the answer
final_answer = first_sentence + ' ' + emojis
```

## License

This project is licensed under the MIT License.

## Contact

If you have any questions or suggestions, you contact me at fribetto(at)gmail(dot)com.
