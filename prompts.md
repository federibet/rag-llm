# Prompts for Cohere API

## Prompt for Generating Answer
The following prompt is used to generate answers based on the document context and user question:

```
Contexto: {most_relevant_chunk}
Pregunta: {user_question}
Responde en español y en tercera persona en una oración.
```

## Prompt for Generating Emojis
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
