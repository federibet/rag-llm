# Prompts for Cohere API

## Prompt for Generating Answer
The following prompt is used to generate answers based on the document context and user question:

```
Contexto: {most_relevant_chunk}
Pregunta: {user_question_translated}
Respuesta en tercera persona y en una oración, añadiendo (después del punto final) dos emojis que representen esta respuesta:
```

### Example Usage in Code

Here is how the prompt is used in the `app.py` script:

```python
# Create a prompt for the LLM
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
```
