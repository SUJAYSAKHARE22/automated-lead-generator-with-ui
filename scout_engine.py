import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import re
from urllib.parse import urlparse


class ScoutEngine:
    def __init__(self, company_desc):
        print("⏳ Loading local similarity model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.my_embedding = self.model.encode(company_desc, convert_to_tensor=True)
        self.my_desc = company_desc

    # ---------------- TEXT CLEANING ---------------- #
    def get_clean_text(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code != 200:
                return ""

            soup = BeautifulSoup(resp.text, 'html.parser')

            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            return re.sub(r'\s+', ' ', soup.get_text())[:4000]

        except Exception:
            return ""

    # ---------------- META DESCRIPTION ---------------- #
    def extract_meta_description(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')

            meta_desc = soup.find("meta", attrs={"name": "description"})
            if not meta_desc:
                meta_desc = soup.find("meta", attrs={"property": "og:description"})

            if meta_desc:
                return meta_desc.get("content", "").strip()

            p = soup.find('p')
            return p.get_text().strip()[:200] if p else "No description found."

        except Exception:
            return "Could not retrieve description."

    # ---------------- 🔗 DEEP CRAWLER ---------------- #
    def find_company_links(self, hub_url):
        """
        Extracts REAL company links from blogs, listicles, directories.
        """
        print(f"🔗 Extracting company links from: {hub_url}")

        links = []

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(hub_url, headers=headers, timeout=10)

            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            hub_domain = urlparse(hub_url).netloc

            for a in soup.find_all('a', href=True):
                link = a['href']

                if not link.startswith('http'):
                    continue

                # Skip same-domain links
                if hub_domain in link:
                    continue

                # Skip social/media/noise
                if any(x in link.lower() for x in [
                    "facebook", "twitter", "linkedin",
                    "youtube", "instagram", "google",
                    "wikipedia"
                ]):
                    continue

                links.append(link)

            return list(set(links))[:15]

        except Exception:
            return []

    # ---------------- AI SIMILARITY ---------------- #
    def calculate_match(self, lead_text):
        if not lead_text or len(lead_text) < 100:
            return 0

        lead_embedding = self.model.encode(lead_text, convert_to_tensor=True)
        return round(util.cos_sim(self.my_embedding, lead_embedding).item() * 100, 2)

    # ---------------- STATIC PITCH ---------------- #
    def generate_static_pitch(self, score):
        if score > 50:
            return (
                f"Highly relevant match! Our services in "
                f"{self.my_desc[:50]} align perfectly with your work."
            )

        return "Relevant match. We can help automate your workflows."
