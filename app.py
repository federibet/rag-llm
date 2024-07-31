from flask import Flask, request, jsonify, Response
import cohere
import chromadb
import uuid
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import logging
import emoji

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Cohere
cohere_api_key = 'znMajXo63oZ1RCuBXBhFNhm6iW7toDPbjxBJTiSg'
co = cohere.Client(cohere_api_key)

# Initialize ChromaDB Client
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="document_embeddings")

# Cache to store answers to questions
answer_cache = {}

# Function to read the entire document from a DOCX file
def read_document_from_docx(file_path):
    doc = Document(file_path)
    return '\n\n'.join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

# Read and process the document
def process_document(file_path):
    content = read_document_from_docx(file_path)
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=200, chunk_overlap=30)
    docs = text_splitter.create_documents([content])
    
    # Store chunks in ChromaDB
    for doc in docs:
        uuid_name = str(uuid.uuid1())
        try:
            embedding = co.embed(texts=[doc.page_content], model='large').embeddings[0]  # Get the embedding
            collection.add(ids=[uuid_name], documents=[doc.page_content], metadatas=[{'text': doc.page_content}], embeddings=[embedding])
        except Exception as e:
            logging.error(f"Error getting embedding: {e}")

# Initialize the document processing
file_path = 'documento.docx'  # Update with your DOCX file path
try:
    process_document(file_path)
except Exception as e:
    logging.error(f"Error processing document: {e}")

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Get the user's name and question from the request
        user_name = request.json.get('user_name')
        user_question = request.json.get('question')

        # Check if the answer is already cached
        if user_question in answer_cache:
            cached_answer = answer_cache[user_question]
            response_data = {
                'user_name': user_name,
                'question': user_question,
                'answer': cached_answer
            }
            return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')

        # Step 1: Retrieve the most relevant chunk using Chroma
        question_embedding = co.embed(texts=[user_question], model='large').embeddings[0]  # Get the embedding for the question
        results = collection.query(query_embeddings=[question_embedding], n_results=1)

        # Extract the most relevant chunk
        most_relevant_chunk = results['documents'][0][0]  # Access the first document in the first list

        # Step 2: Create a prompt for the LLM
        prompt = f"Contexto: {most_relevant_chunk}\nPregunta: {user_question}\nResponde en tercera persona y en una oración:"  # Added "Responde en tercera persona"

        # Step 3: Use the Cohere LLM to get an answer
        response = co.generate(prompt=prompt, model='command', max_tokens=150)  # Adjust parameters as needed
        generated_answer = response.generations[0].text.strip()

        # Extract only the first sentence from the generated answer
        first_sentence = generated_answer.split('.')[0] + '.'

        # Step 4: Create a prompt to generate emojis based on the answer
        emoji_prompt = f"Answer: {first_sentence}\nAdd two or three emojis that represent this answer:"

        # Step 5: Use the Cohere LLM to generate emojis
        emoji_response = co.generate(prompt=emoji_prompt, model='command', max_tokens=10)
        emoji_text = emoji_response.generations[0].text.strip()

        # Filter to keep only emojis
        emojis = ''.join([char for char in emoji_text if emoji.is_emoji(char)])

        # Append emojis to the answer
        final_answer = first_sentence + ' ' + emojis

        # Cache the generated answer
        answer_cache[user_question] = final_answer

        # Create the response data
        response_data = {
            'user_name': user_name,
            'question': user_question,
            'answer': final_answer
        }

        # Return the generated answer along with the user's name, ensuring no special character escaping
        return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')
    except Exception as e:
        logging.error(f"Error in ask endpoint: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        logging.error(f"Error starting Flask app: {e}")
