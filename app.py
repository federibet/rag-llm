from flask import Flask, request, jsonify, Response
import cohere
import chromadb
import uuid
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import logging
import emoji
import requests
from langdetect import detect, detect_langs

app = Flask(__name__)

########################## Agregar que si no es uno de los tres idiomas, que use español

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize Cohere
cohere_api_key = 'pfK329FllWHqYXfGP0mwHi79OQEU1ehVMJV6PvPH'  # Replace with your Cohere API key
co = cohere.Client(cohere_api_key)

# Initialize ChromaDB Client
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="document_embeddings")

# Cache to store answers to questions
answer_cache = {}

# Function to read the entire document from a DOCX file and detect its language
def read_document_from_docx(file_path):
    doc = Document(file_path)
    content = '\n\n'.join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
    detected_languages = detect_langs(content)
    # Assuming the first detected language is the main language of the document
    main_language = detected_languages[0].lang if detected_languages else 'en'
    return content, main_language

# Read and process the document
def process_document(file_path):
    content, doc_language = read_document_from_docx(file_path)
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n"], chunk_size=200, chunk_overlap=30)
    docs = text_splitter.create_documents([content])
    
    # Store chunks in ChromaDB with language metadata
    for doc in docs:
        uuid_name = str(uuid.uuid1())
        try:
            embedding = co.embed(texts=[doc.page_content], model='large').embeddings[0]  # Get the embedding
            collection.add(
                ids=[uuid_name],
                documents=[doc.page_content],
                metadatas=[{'text': doc.page_content, 'language': doc_language}],
                embeddings=[embedding]
            )
        except Exception as e:
            logging.error(f"Error getting embedding: {e}")

# Initialize the document processing
file_path = 'documento.docx'  # Update with your DOCX file path
try:
    process_document(file_path)
except Exception as e:
    logging.error(f"Error processing document: {e}")

def translate_text(text, source_language, target_language):
    url = "https://api.mymemory.translated.net/get"
    params = {
        'q': text,
        'langpair': f'{source_language}|{target_language}'
    }
    response = requests.get(url, params=params)
    response_data = response.json()
    return response_data['responseData']['translatedText']

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Get the user's name and question from the request
        user_name = request.json.get('user_name')
        user_question = request.json.get('question')

        # Detect the language of the user's question
        detected_question_language = detect(user_question)
        logging.info(f"Detected question language: {detected_question_language}")

        # Detect the language of the document
        document_content, detected_document_language = read_document_from_docx(file_path)
        logging.info(f"Detected document language: {detected_document_language}")

        # Translate the question to the document's language for processing if necessary
        if detected_question_language != detected_document_language:
            user_question_translated = translate_text(user_question, detected_question_language, detected_document_language)
        else:
            user_question_translated = user_question
        
        logging.info(f"Translated question: {user_question_translated}")

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
        question_embedding = co.embed(texts=[user_question_translated], model='large').embeddings[0]
        results = collection.query(query_embeddings=[question_embedding], n_results=1)

        logging.debug(f"Results from ChromaDB query: {results}")

        # Extract the most relevant chunk directly
        if results['documents'] and results['documents'][0]:
            most_relevant_chunk = results['documents'][0][0]
        else:
            logging.error("No relevant chunk found for the detected language.")
            return jsonify({'error': 'No relevant chunk found for the detected language.'}), 500

        # Combine steps 2 and 4 into a single prompt
        combined_prompt = f"Contexto: {most_relevant_chunk}\nPregunta: {user_question_translated}\nRespuesta en tercera persona y en una oración, añadiendo (después del punto final) dos emojis que representen esta respuesta:"

        # Use the Cohere LLM to get an answer with emojis
        response = co.generate(prompt=combined_prompt, model='command', max_tokens=160)
        logging.debug(f"Response from Cohere LLM: {response}")

        generated_answer = response.generations[0].text.strip()

        # Extract only the first sentence from the generated answer
        first_sentence = generated_answer.split('.')[0] + '.'

        # Filter to keep only emojis from the generated answer
        emojis = ''.join([char for char in generated_answer if emoji.is_emoji(char)])

        # Append emojis to the answer
        final_answer = first_sentence + ' ' + emojis

        # Translate the final answer back to the question's language if necessary
        if detected_question_language != detected_document_language:
            final_answer = translate_text(final_answer, detected_document_language, detected_question_language)
        logging.info(f"Generated final answer: {final_answer}")

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
        # Detect the document's language during initialization
        document_content, document_language = read_document_from_docx(file_path)
        logging.info(f"Document language detected during initialization: {document_language}")

        # Process the document
        process_document(file_path)

        app.run(debug=True)
    except Exception as e:
        logging.error(f"Error starting Flask app: {e}")