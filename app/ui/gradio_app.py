import gradio as gr
import requests

SEARCH_API_URL = "http://localhost:8000/api/products/search"
CHATBOT_API_URL = "http://localhost:8000/api/chatbot"

def search_products(query):
    # You can add more params if needed (variant, price, etc.)
    params = {"name": query}
    resp = requests.get(SEARCH_API_URL, params=params)
    if resp.status_code == 200:
        products = resp.json()
        if not products:
            return "No products found."
        return "\n\n".join(
            [f"{p['name']} (₹{p['price']}) [Variant: {p.get('variant','-')}, Sizes: {', '.join(p.get('sizes') or [])}]" for p in products]
        )
    else:
        return f"Error: {resp.status_code} - {resp.text}"

def chatbot_response(message):
    resp = requests.post(CHATBOT_API_URL, json={"message": message})
    if resp.status_code == 200:
        return resp.json().get("reply", "No reply")
    else:
        return f"Error: {resp.status_code} - {resp.text}"

with gr.TabbedInterface(["Product Search", "Chatbot"]) as tabs:
    with tabs.tab("Product Search"):
        gr.Interface(
            fn=search_products,
            inputs=gr.Textbox(label="Search for products (name, keyword, etc.)"),
            outputs="text",
            title="Product Search"
        )
    with tabs.tab("Chatbot"):
        gr.Interface(
            fn=chatbot_response,
            inputs=gr.Textbox(label="Ask anything about products or orders"),
            outputs="text",
            title="E-Commerce Chatbot"
        )

if __name__ == "__main__":
    tabs.launch()
