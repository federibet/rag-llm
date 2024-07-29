from flask import Flask, request, jsonify
import cohere

app = Flask(__name__)

# Initialize Cohere client
cohere_api_key = 'znMajXo63oZ1RCuBXBhFNhm6iW7toDPbjxBJTiSg'
co = cohere.Client(cohere_api_key)

@app.route('/ask', methods=['POST'])
def ask_cohere():
    # Parse the incoming JSON request
    data = request.get_json()

    # Ensure the required fields are present
    if not data or 'user_name' not in data or 'question' not in data:
        return jsonify({"error": "Invalid request format. Must include 'user_name' and 'question'."}), 400

    user_name = data['user_name']
    question = data['question']

    # Communicate with Cohere's API
    try:
        response = co.generate(
            model='command-xlarge-nightly',  # Specify the Cohere model you wish to use
            prompt=f"{question}",
            max_tokens=50,  # Adjust the number of tokens as needed
        )
        cohere_response = response.generations[0].text.strip()
    except Exception as e:
        return jsonify({"error": f"Failed to communicate with Cohere API: {str(e)}"}), 500

    # Return the response from Cohere
    return jsonify({
        "user_name": user_name,
        "question": question,
        "response": cohere_response
    })

if __name__ == '__main__':
    app.run(debug=True)