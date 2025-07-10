import gradio as gr
import requests

# ---- API Endpoints ----
CHATBOT_API_URL = "http://localhost:8000/chatbot"  # Update if needed
PRODUCT_SEARCH_API_URL = "http://localhost:8000/products/search"  # Update if needed

# ---- Chatbot Logic (messages format for Gradio v4+) ----
def chat_with_backend(messages, state=None):
    user_message = messages[-1]["content"]
    try:
        response = requests.post(
            CHATBOT_API_URL,
            json={"message": user_message},
            timeout=10
        )
        response.raise_for_status()
        reply = response.json().get("reply", "No reply from backend.")
    except Exception as e:
        reply = f"Error: {e}"
    return messages + [{"role": "assistant", "content": reply}]

# ---- Product Search Logic ----
def search_products(name, variant, min_price, max_price):
    params = {}
    if name: params["name"] = name
    if variant: params["variant"] = variant
    if min_price is not None: params["min_price"] = min_price
    if max_price is not None: params["max_price"] = max_price
    try:
        resp = requests.get(PRODUCT_SEARCH_API_URL, params=params, timeout=10)
        if resp.ok:
            products = resp.json()
            if not products:
                return "No products found."
            cards = []
            for p in products:
                card = f"### {p.get('name', '-')}\n"
                card += f"**Price:** ₹{p.get('price', '-')}\n\n"
                card += f"**Variant:** {p.get('variant', '-')}\n\n"
                card += f"**Sizes:** {', '.join(p.get('sizes', []))}\n\n"
                card += f"**Description:** {p.get('description', '-')}\n\n"
                if p.get("main_image"):
                    card += f"![Product Image]({p['main_image']})\n"
                card += "---\n"
                cards.append(card)
            return "\n".join(cards)
        else:
            return f"API error: {resp.text}"
    except Exception as e:
        return f"Error: {e}"

# ---- Gradio UI ----
with gr.Blocks(title="🛍️ Zupain Clothing Assistant") as gradio_app:
    gr.Markdown("# 🛍️ Zupain Clothing Assistant")
    gr.Markdown(
        "Welcome! Ask about our latest kurtas, dresses, sizes, prices, or get recommendations for girls' clothing.\n\n"
        "Use the **Chatbot** for natural questions, or the **Product Search** tab to filter and browse our collection."
    )

    with gr.Tab("Chatbot"):
        gr.ChatInterface(
            fn=chat_with_backend,
            examples=[
                [{"role": "user", "content": "Show me red kurtas for girls under ₹1000"}],
                [{"role": "user", "content": "What sizes are available for the blue floral kurta?"}],
                [{"role": "user", "content": "Are there any discounts on cotton kurtas?"}],
                [{"role": "user", "content": "Recommend some party wear dresses for girls"}],
                [{"role": "user", "content": "Do you have pink kurtas in size M?"}],
                [{"role": "user", "content": "What is the price of the Anarkali kurta?"}],
                [{"role": "user", "content": "Show me the latest arrivals in girls' kurtas"}],
                [{"role": "user", "content": "Which kurtas are available in XXL?"}],
                [{"role": "user", "content": "Do you have matching leggings for kurtas?"}],
                [{"role": "user", "content": "Tell me about trending ethnic wear for girls"}]
            ],
            type="messages"
        )

    with gr.Tab("Product Search"):
        with gr.Row():
            name = gr.Textbox(label="Product Name or Keyword", scale=2, placeholder="e.g. kurta, dress, floral, etc.")
            variant = gr.Textbox(label="Variant (optional)", scale=1, placeholder="e.g. red, cotton, etc.")
        with gr.Row():
            min_price = gr.Number(label="Min Price", scale=1)
            max_price = gr.Number(label="Max Price", scale=1)
        search_btn = gr.Button("Search Products")
        results = gr.Markdown()

        search_btn.click(
            search_products,
            [name, variant, min_price, max_price],
            results
        )

# Optional: allow standalone running
if __name__ == "__main__":
    gradio_app.launch()
