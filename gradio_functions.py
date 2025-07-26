import os


def setup_open_ai():
    """
    Setup function for OpenAI API
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    client = openai.OpenAI(api_key=openai_api_key)
    return client

def save_results_to_supabase(comment: str, 
        customer_analysis: str, 
        product_feedback: str):
    """
    Save result to Supabase table
    """
    pass

def ai_analyze_comments(client,
        prompt: str, 
        comment: str,
        debug: bool = True, 
        gpt_model="gpt-3.5-turbo"
        ) -> str:
    """
    Sends `prompt` plus the JSON version of `df` to ChatGPT,
    and returns the model's response.strip()
    """

    if debug:
        print("Prompt sent to model:\n", prompt)

    c_messages = [
    {"role": "system",
    "content": 
        "You are an expert linguistic analyst specializing in extracting and scoring themes from customer return comments. "
        "You always return your output exactly in the structure specified in the user's instructions. "
        "Be precise, consistent, and strictly follow the output schema and scoring rules provided."
        },
        {"role": "user", "content": prompt},
        {"role": "user", "content": comment}
    ]

    resp = client.chat.completions.create(
        model=gpt_model,
        messages=c_messages,
        temperature=0.1,
        max_tokens=15000,
    )

    content = resp.choices[0].message.content.strip()

    if debug:
        print("Raw response from OpenAI:\n", content)
    if not content:
        raise ValueError("Empty response from OpenAI")

    return content


