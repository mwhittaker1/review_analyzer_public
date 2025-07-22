import gradio as gr
import pandas as pd
import duckdb
from typing import Optional, Tuple
import openpyxl

def get_comment(comment: str) -> str:
    """
    Listener function to accept comment from the user
    'Comment' is string of user input
    """
    # command logic here
    
    if comment == "":
        return "No comment provided."
    elif not isinstance(comment, str):
        return f"{comment} is not a valid entry."
    
    return f"Comment received: {comment}"

def setup_open_ai():
    """
    Setup function for OpenAI API
    """
    # initialization logic here
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

    messages = [
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
        messages=messages,
        temperature=0.1,
        max_tokens=15000,
    )

    content = resp.choices[0].message.content.strip()

    if debug:
        print("Raw response from OpenAI:\n", content)
    if not content:
        raise ValueError("Empty response from OpenAI")

    return content

def save_results_to_supabase(comment: str, 
        customer_analysis: str, 
        product_feedback: str):
    """
    Save result to Supabase table
    """
    pass

def main():
    """
    insert text here later
    """

    # General workflow

    # Collect example comment from user

    # Check if comment is valid

    # prepare open AI client

    # Send comment to AI client for customer retur analysis

    # Send comment to AI client for Product feedback analysis

    # Format response from AI Client

    # Display results to user

    # Log results in supabase

# iface = gr.Interface(
#     fn=get_comment,
#     inputs=gr.Textbox(label=f"Enter an example return comment.\nfor instance:\n'The shirt was too small, and the fabric was not what I expected. I liked the style though!' "),
#     outputs="text"
# )
# iface.launch()

example_comments = [
    ["The shirt was too small, and the fabric was not what I expected. I liked the style though!"],
    ["Shoes were uncomfortable, but delivery was fast."],
    ["You sent me the wrong item"],
    ["too small"]
]
example_df = pd.DataFrame(example_comments, columns=["Example Comments"])

with gr.Blocks() as demo:
    gr.Markdown("## Enter an example return comment")
    comment_box = gr.Textbox(label="Comment")
    output_text = gr.Textbox(label="Output")
    gr.Dataframe(value=example_df, label="Example Comments", interactive=False)
    comment_box.submit(get_comment, inputs=comment_box, outputs=output_text)

demo.launch()