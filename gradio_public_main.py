import gradio as gr
import pandas as pd
import duckdb
from typing import Optional, Tuple
import openpyxl
from dotenv import load_dotenv
import openai
import gradio_functions as gf
load_dotenv()

def get_comment(comment: str) -> tuple:
    """
    Listener function to accept comment from the user
    'Comment' is string of user input
    """
    # command logic here
    
    if comment == "":
        return "No comment provided."
    elif not isinstance(comment, str):
        return f"{comment} is not a valid entry."
    
    customer_analysis= f"Analyzing customer return comment: {comment}"
    product_feedback = f"Analyzing product feedback comment: {comment}"

    return customer_analysis, product_feedback

def main():
    """
    insert text here later
    """

    # General workflow

    # Collect example comment from user
    ## get_comment

    # Check if comment is valid
    ## get_comment

    # prepare open AI client
    ## gf.setuo_open_ai

    # Send comment to AI client for customer retur analysis
    # ai_analyze_comments
    # Send comment to AI client for Product feedback analysis

    # Format response from AI Client

    # Display results to user

    # Log results in supabase


example_comments = [
    ["The shirt was too small, and the fabric was not what I expected. I liked the style though!"],
    ["Shoes were uncomfortable, but delivery was fast."],
    ["You sent me the wrong item"],
    ["too small"]
]
example_df = pd.DataFrame(example_comments, columns=["Example Comments"])

with gr.Blocks() as demo:
    gr.Markdown("## Enter an example return comment")
    comment_box = gr.Textbox(label="Insert an example return comment")
    output_text_customer = gr.Textbox(label="Anaylzed Comment")
    output_text_product = gr.Textbox(label="Anaylzed Comment")
    gr.Dataframe(value=example_df, label="Example Comments", interactive=False)
    comment_box.submit(get_comment, inputs=comment_box, outputs=(output_text_customer, output_text_product))

demo.launch()