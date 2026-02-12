from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime

from search_agent import SearchAgent
from scout_engine import ScoutEngine
from scraper.scraper import scrape_website

app = Flask(__name__)

# Configuration
PROCESSED_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'processed')


# ---------------- PARSING ---------------- #
def parse_company_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        filename = os.path.basename(file_path)
        company_name = filename.replace('.txt', '')

        company_data = {
            'name': company_name,
            'file': filename,
            'raw_content': content,
            'website': '',
            'description': '',
            'services': [],
            'team': {},
            'emails': [],
            'phones': []
        }

        import re

        website_match = re.search(r'Website:\s*(https?://[^\n]+)', content)
        if website_match:
            company_data['website'] = website_match.group(1).strip()

        desc_match = re.search(r'Description:\s*([^\n]+)', content)
        if desc_match:
            company_data['description'] = desc_match.group(1).strip()

        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        company_data['emails'] = list(set(re.findall(email_pattern, content)))

        phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,4}(?:[-\s\.]?[0-9]{1,6})?'
        phones_found = re.findall(phone_pattern, content)
        company_data['phones'] = list(set([p.strip() for p in phones_found if len(p) > 5]))

        return company_data

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def get_all_companies():
    companies = []

    if os.path.exists(PROCESSED_DATA_PATH):
        for filename in sorted(os.listdir(PROCESSED_DATA_PATH)):
            if filename.endswith('.txt'):
                file_path = os.path.join(PROCESSED_DATA_PATH, filename)
                company_data = parse_company_data(file_path)
                if company_data:
                    companies.append(company_data)

    return companies


# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    companies = get_all_companies()
    return render_template('index.html', companies=companies, total=len(companies))


@app.route('/company/<company_name>')
def company_detail(company_name):
    companies = get_all_companies()
    company = next((c for c in companies if c['name'] == company_name), None)

    if not company:
        return "Company not found", 404

    return render_template('company_detail.html', company=company)


# 🚀 NEW DEEP DISCOVERY SEARCH
@app.route('/search', methods=['POST'])
def search_and_scrape():
    data = request.get_json()

    query = data.get("query")
    num_results = int(data.get("num_results", 5))

    if not query:
        return jsonify({"error": "Query required"}), 400

    print(f"\n🚀 Starting Deep Lead Discovery for: {query}")

    # Your service description for similarity scoring
    company_desc = "AI Automation and Python Services"

    scout = ScoutEngine(company_desc)
    searcher = SearchAgent()

    # STEP 1 — Find hub/listicle URLs from search
    hub_urls = searcher.find_company_urls(query, num_results)

    print("📂 Hub URLs found:", hub_urls)

    discovered_sites = set()

    # STEP 2 — Deep crawl hubs → real company websites
    for hub in hub_urls:
        print(f"🔗 Crawling hub: {hub}")
        links = scout.find_company_links(hub)
        discovered_sites.update(links)

    print(f"🔎 Total candidate company sites: {len(discovered_sites)}")

    # STEP 3 — AI relevance filtering
    final_sites = []

    for url in discovered_sites:
        text = scout.get_clean_text(url)
        if not text:
            continue

        score = scout.calculate_match(text)

        if score > 30:
            print(f"✨ Relevant ({score}%): {url}")
            final_sites.append(url)

        if len(final_sites) >= num_results:
            break

    # STEP 4 — Scrape structured info
    scraped = []

    for url in final_sites:
        try:
            scrape_website(url)
            scraped.append(url)
        except Exception as e:
            print("❌ Scrape failed:", url, e)

    return jsonify({
        "message": "Deep discovery & scraping complete",
        "total_found": len(final_sites),
        "scraped": scraped
    })


# ---------------- RUN ---------------- #
if __name__ == '__main__':
    app.run(debug=True, port=5000)
