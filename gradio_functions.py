import os
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv

def check_comment(comment: str) -> tuple:
    """
    Performs basic validation (checks empty)
    """
    # command logic here
    
    if comment == "":
        return "No comment provided."
    elif not isinstance(comment, str):
        return f"{comment} is not a valid entry."
    
    c_comment = comment.strip()

    return 

def save_results_to_supabase(comment: str, 
        customer_analysis: str, 
        product_feedback: str):
    """
    Save result to Supabase table
    """
    pass

def ai_analyze_comments(
        comment: str,
        c_prompt: str,
        p_prompt: str,
        debug: bool = True,
        gpt_model="gpt-3.5-turbo"
        ) -> str:
    """
    Sends `prompt` plus the JSON version of `df` to ChatGPT,
    and returns the model's response.strip()
    """
    api_key = os.getenv("OPEN_API_KEY")
    client = OpenAI(api_key=api_key)

    c_messages = [
    {"role": "system",
    "content": 
        "You are an expert linguistic analyst specializing in extracting and scoring themes from customer return comments. "
        "You always return your output exactly in the structure specified in the user's instructions. "
        "Be precise, consistent, and strictly follow the output schema and scoring rules provided."
        },
        {"role": "user", "content": c_prompt},
        {"role": "user", "content": comment}
    ]

    c_resp = client.chat.completions.create(
        model=gpt_model,
        messages=c_messages,
        temperature=0.1,
        max_tokens=250,
    )

    p_messages = [
    {"role": "system",
    "content": 
        "You are an expert linguistic analyst specializing in extracting and scoring themes from customer return comments. "
        "You always return your output exactly in the structure specified in the user's instructions. "
        "Be precise, consistent, and strictly follow the output schema and scoring rules provided."
        },
        {"role": "user", "content": p_prompt},
        {"role": "user", "content": comment}
    ]

    p_resp = client.chat.completions.create(
        model=gpt_model,
        messages=p_messages,
        temperature=0.1,
        max_tokens=250,
    )

    if hasattr(c_resp.choices[0], "finish_reason") and c_resp.choices[0].finish_reason == "length":
        c_content = "[ERROR] Max tokens reached for customer analysis. Response may be incomplete."
    else:
        c_content = c_resp.choices[0].message.content.strip()

    if debug:
        print("Raw response from OpenAI:\n", c_content)
    if not c_content:
        raise ValueError("Empty response from OpenAI")
    
    if hasattr(p_resp.choices[0], "finish_reason") and p_resp.choices[0].finish_reason == "length":
        p_content = "[ERROR] Max tokens reached for product analysis. Response may be incomplete."
    else:
        p_content = p_resp.choices[0].message.content.strip()

    if debug:
        print("Raw response from OpenAI:\n", p_content)
    if not p_content:
        raise ValueError("Empty response from OpenAI")

    print(f"Customer Analysis:\n{c_content}\n")
    print(f"Product Feedback:\n{p_content}\n")

    return c_content, p_content

####

def run_comment_analysis(comment: str) -> tuple:
    """
    Main function to run comment analysis workflow.
    """

    # c_temp = "Your customer feedback analysis will appear here"
    # p_temp = "Your product feedback analysis will appear here"

    # yield  c_temp, p_temp

    check_comment(comment)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # # Prepare prompt for customer return analysis
    with open("prompts/customer_sentiment_prompt.txt", "r", encoding="utf-8") as f:
        c_prompt = f.read()

    # Prepare prompt for product feedback analysis
    with open("prompts/product_prompt.txt", "r", encoding="utf-8") as f:
        p_prompt = f.read()

    print(f"Prompt, comment sent to model:\n{c_prompt}\n{p_prompt}\n{comment}")

    # # Analyze customer return comment
    c_analysis, p_analysis = ai_analyze_comments(comment, c_prompt, p_prompt, debug=True, gpt_model="gpt-3.5-turbo")

    return c_analysis, p_analysis
    
if __name__ == "__main__":
    run_comment_analysis("This is a test comment for analysis.")