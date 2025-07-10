import asyncio
import json
import os
import random
from datetime import datetime
from urllib.parse import urlparse, urljoin

from playwright.async_api import async_playwright
from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from Zupain2.weaviate_zupain import upsert_weaviate_product

# --- ENV and DB/Weaviate Setup ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.product import Product  # Adjust if your import path differs

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- Data Cleaning Helpers ---
def clean_price(value):
    try:
        return float(value.replace("₹", "").replace(",", "").strip())
    except:
        return None

def clean_discount(value):
    try:
        return float(value.split('%')[0].strip())
    except:
        return None

def process_product_fields(prod):
    return {
        "id": prod.get("id"),
        "url": prod.get("url"),
        "name": prod.get("name"),
        "price": clean_price(prod.get("price", "")),
        "old_price": clean_price(prod.get("old_price", "")),
        "discount": clean_discount(prod.get("discount", "")),
        "variant": prod.get("variant"),
        "sizes": [str(s) for s in prod.get("sizes", [])] if isinstance(prod.get("sizes"), list) else [],
        "description": prod.get("description"),
        "main_image": prod.get("main_image"),
        "last_updated": datetime.utcnow().isoformat(),
        "category": prod.get("category"),
        "subcategory": prod.get("subcategory"),
        "video": prod.get("video"),
        "seo_title": prod.get("seo_title"),
        "seo_description": prod.get("seo_description"),
    }


# --- Crawler Constants ---
START_URL = "https://preprod-arunodayakurtis.zupain.com/"
DOMAIN = urlparse(START_URL).netloc
BASE_URL = "https://preprod-arunodayakurtis.zupain.com"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
]

def is_product_url(url):
    parsed = urlparse(url)
    return parsed.netloc == DOMAIN and "/pd/" in parsed.path

def get_results_folder():
    now = datetime.now()
    folder = f"zupain2/results-{now.day}-{now.strftime('%B').lower()}-{now.strftime('%y')}-{now.strftime('%I-%M%p').lower()}"
    os.makedirs(folder, exist_ok=True)
    return folder

# --- Crawl all category/subcategory URLs ---
async def crawl_all_product_urls_from_sidebar(start_url, base_url, domain):
    product_urls = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await page.goto(start_url)
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)  # Let sidebar render

        # Find all sidebar category elements
        category_selectors = await page.query_selector_all("div.ant-menu-submenu-title")
        print(f"Found {len(category_selectors)} sidebar categories.")

        for idx, cat in enumerate(category_selectors):
            try:
                await cat.click()
                await asyncio.sleep(2)  # Wait for products to load

                # Scrape product links from the product grid
                links = await page.eval_on_selector_all(
                    "a[href*='/pd/']", "els => els.map(a => a.href)"
                )
                for link in links:
                    if is_product_url(link):
                        product_urls.add(link.split("#")[0].rstrip("/"))
                print(f"Category {idx+1}: found {len(links)} products.")
            except Exception as e:
                print(f"Error scraping category {idx}: {e}")

        await browser.close()
    return sorted(product_urls)


# --- Crawl all product URLs for a given category ---
async def crawl_product_urls_for_category(start_url, base_url, domain):
    product_urls = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await page.goto(start_url)
        page_num = 1
        while True:
            print(f"[{start_url}] [Page {page_num}] Crawling: {page.url}")
            try:
                await page.wait_for_selector("a[href*='/pd/']", timeout=20000)
            except Exception:
                break
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)
            links = await page.eval_on_selector_all(
                "a[href*='/pd/']", "els => els.map(a => a.getAttribute('href'))"
            )
            full_links = [urljoin(base_url, link) for link in links if link]
            for link in full_links:
                if is_product_url(link):
                    product_urls.add(link.split("#")[0].rstrip("/"))
            # Pagination
            next_btn = await page.query_selector(
                '.pagination-next, .next, [aria-label="Next"], button[aria-label="Next"]'
            )
            if next_btn and await next_btn.is_enabled():
                await next_btn.click()
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(random.uniform(1.0, 2.0))
                page_num += 1
            else:
                break
        await context.close()
        await browser.close()
    return product_urls

# --- Product Extraction ---
async def get_first_text(page, selectors):
    for sel in selectors:
        try:
            text = await page.eval_on_selector(sel, "el => el.textContent")
            if text and text.strip():
                return text.strip()
        except:
            continue
    return ""

async def robust_get_text(page, selectors, retries=3, delay=1.5):
    for _ in range(retries):
        text = await get_first_text(page, selectors)
        if text:
            return text
        await asyncio.sleep(delay)
    return ""

async def extract_product_details(product_urls, results_folder):
    import os
    products = []
    start_time = datetime.now()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))

        async def scrape_product(idx_url):
            idx, url = idx_url
            page = await context.new_page()
            product = {"url": url}
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("domcontentloaded")
                await asyncio.sleep(1.5)

                product["name"] = await robust_get_text(page, [
                    "p[style*='font-size: 29px']",
                    "h6",
                    "h1",
                    "h2",
                    "p[style*='font-weight: 600']",
                    "title"
                ])
                product["price"] = await robust_get_text(page, [
                    "p[style*='font-size: 18px'][style*='font-weight: 700']",
                    "p[style*='font-weight: 700']"
                ])
                product["old_price"] = await robust_get_text(page, [
                    "p[style*='text-decoration-line: line-through']"
                ])
                product["discount"] = await robust_get_text(page, [
                    "p[style*='color: rgb(255, 160, 95)']",
                    "p[style*='OFFER']",
                    "p[style*='offer']"
                ])
                product["variant"] = await robust_get_text(page, [
                    ".mt-10 h6",
                    "h6"
                ])
                try:
                    product["sizes"] = await page.eval_on_selector_all(
                        ".mt-10 button span", "els => els.map(e => e.textContent.trim())"
                    )
                except:
                    product["sizes"] = []
                product["description"] = await robust_get_text(page, [
                    ".ql-editor",
                    "div[style*='ql-editor']",
                    "div[style*='description']"
                ])
                try:
                    product["main_image"] = await page.eval_on_selector(
                        ".image-display-container img", "el => el.getAttribute('src')"
                    )
                except:
                    product["main_image"] = ""
                product["category"] = await robust_get_text(page, [
                    ".breadcrumb li:nth-child(2)",
                ])
                product["subcategory"] = await robust_get_text(page, [
                    ".breadcrumb li:nth-child(3)",
                ])
                product["video"] = await robust_get_text(page, [
                    "video source",
                ])
                product["seo_title"] = await robust_get_text(page, [
                    "head > title",
                ])
                product["seo_description"] = await robust_get_text(page, [
                    "meta[name='description']",
                ])
                # Save debug HTML if almost everything is missing
                if not any([product.get("name"), product.get("price"), product.get("old_price"),
                            product.get("discount"), product.get("variant"),
                            product.get("description"), product.get("main_image")]):
                    html = await page.content()
                    debug_dir = os.path.join(results_folder, "debug_html")
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(f"{debug_dir}/debug_{idx}.html", "w", encoding="utf-8") as f:
                        f.write(html)
            except Exception as e:
                product["error"] = str(e)
            finally:
                await page.close()
            print("Extracted product:", product)
            return product

        # (Optional: For testing, limit to 5 products)
        # product_urls = product_urls[:5]

        results = []
        for i, url in enumerate(tqdm(product_urls, ncols=100, desc="Progress")):
            result = await scrape_product((i, url))
            results.append(result)
        products = results
        await context.close()
        await browser.close()
    elapsed = (datetime.now() - start_time).total_seconds()
    with open(f"{results_folder}/products.json", "w") as f:
        json.dump(products, f, indent=2)
    print(f"\nExtracted details for {len(products)} products in {elapsed:.1f} seconds.")
    print(f"Saved to {results_folder}/products.json")
    return products

# --- DB and Weaviate Upsert ---
def upsert_product_pg(db, product):
    db_product = db.query(Product).filter(Product.id == product["id"]).first()
    if db_product:
        for k, v in product.items():
            if hasattr(db_product, k):
                setattr(db_product, k, v)
    else:
        db_product = Product(**product)
        db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def upsert_all_products_to_db_and_weaviate(products):
    db = SessionLocal()
    for prod in products:
        product_data = process_product_fields(prod)
        print("About to upsert:", product_data) 
        upsert_product_pg(db, product_data)
        upsert_weaviate_product(product_data)
    db.close()
    print(f"Upserted {len(products)} products to PostgreSQL and Weaviate.")

# --- Main ---
if __name__ == "__main__":
    print("Crawling all product URLs via sidebar categories...")
    all_product_urls = asyncio.run(
        crawl_all_product_urls_from_sidebar(
            "https://preprod-arunodayakurtis.zupain.com/product-list",
            BASE_URL,
            DOMAIN
        )
    )
    print(f"\nTotal unique product URLs found: {len(all_product_urls)}")
    results_folder = get_results_folder()
    with open(f"{results_folder}/product_urls.json", "w") as f:
        json.dump(sorted(all_product_urls), f, indent=2)

    if all_product_urls:
        products = asyncio.run(extract_product_details(sorted(all_product_urls), results_folder))
        with open(f"{results_folder}/products.json", "w") as f:
            json.dump(products, f, indent=2)
        upsert_all_products_to_db_and_weaviate(products)
    else:
        print("No products found! Please check your selectors.")
