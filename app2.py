from flask import Flask, request, jsonify, Response
import cohere
import chromadb
import uuid
import json
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)

# Initialize Cohere
cohere_api_key = 'znMajXo63oZ1RCuBXBhFNhm6iW7toDPbjxBJTiSg'  # Replace with your Cohere API key
co = cohere.Client(cohere_api_key)

# Initialize ChromaDB Client
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="document_embeddings")

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
        embedding = co.embed(texts=[doc.page_content], model='large').embeddings[0]  # Get the embedding
        collection.add(ids=[uuid_name], documents=[doc.page_content], metadatas=[{'text': doc.page_content}], embeddings=[embedding])

# Initialize the document processing
file_path = 'documento.docx'  # Update with your DOCX file path
process_document(file_path)

@app.route('/ask', methods=['POST'])
def ask():
    # Get the user's name and question from the request
    user_name = request.json.get('user_name')
    user_question = request.json.get('question')

    # Step 1: Retrieve the most relevant chunk using Chroma
    question_embedding = co.embed(texts=[user_question], model='large').embeddings[0]  # Get the embedding for the question
    results = collection.query(query_embeddings=[question_embedding], n_results=1)

    # Extract the most relevant chunk
    most_relevant_chunk = results['documents'][0][0]  # Access the first document in the first list

    # Step 2: Create a prompt for the LLM
    prompt = f"Context: {most_relevant_chunk}\nQuestion: {user_question}\nAnswer:"

    # Step 3: Use the Cohere LLM to get an answer
    response = co.generate(prompt=prompt, model='command', max_tokens=150)  # Adjust parameters as needed

    # Create the response data
    response_data = {
        'user_name': user_name,
        'question': user_question,
        'answer': response.generations[0].text.strip()
    }

    # Return the generated answer along with the user's name, ensuring no special character escaping
    return Response(json.dumps(response_data, ensure_ascii=False), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
