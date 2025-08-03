import google.generativeai as genai
import os

api_key = input("Пожалуйста, введите ваш API-ключ: ")
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash-latest')


def load_and_split_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs


file_path = "Resume.text"
paragraphs = load_and_split_text(file_path)


def keyword_retriever(query, paragraphs, top_n=3):
    query_words = set(word.strip(".,!?:") for word in query.lower().split())
    paragraph_scores = []


    for para in paragraphs:
        score = sum(1 for word in query_words if word in para.lower())
        paragraph_scores.append((score, para))


    paragraph_scores.sort(key=lambda x: x[0], reverse=True)
    return [para for score, para in paragraph_scores[:top_n] if score > 0]


def generate_rag_prompt(question, retrieved_context):
    if not retrieved_context:
        context_str = "Контекст не найден."
    else:
        context_str = "\n\n".join(retrieved_context)


    prompt = f"""Опираясь исключительно на следующий контекст, ответь на вопрос пользователя: {question}


Контекст: {context_str}
"""
    return prompt


def ask_gemini(question, context):
    prompt = generate_rag_prompt(question, context)
    chat_session = model.start_chat(history=[{"role": "user", "parts": [prompt]}])


    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Ошибка: {e}"


print("Добро пожаловать в чат с ботом! Введите 'выход' для завершения.")
while True:
    user_input = input("Вы: ")
   
    if user_input.lower() in ['выход', 'exit']:
        print("До свидания!")
        break


    relevant_paragraphs = keyword_retriever(user_input, paragraphs)


    if relevant_paragraphs:
        answer = ask_gemini(user_input, relevant_paragraphs)
        print("Бот:", answer)
    else:
        print("Извините, не найдено релевантных абзацев.")
