from ddgs import DDGS
from urllib.parse import urlparse


class SearchAgent:
    def clean_domain(self, url):
        """Convert any URL into root homepage"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def is_valid_company_site(self, url):
        """Filter out articles, blogs, directories"""
        bad_words = [
            "blog", "news", "article", "post", "insight",
            "medium", "directory", "listing", "top-", "best-",
            "wikipedia", "linkedin", "twitter", "facebook",
            "youtube", "instagram"
        ]

        return not any(word in url.lower() for word in bad_words)

    def find_company_urls(self, query, num_results=10):
        print(f"🌍 Searching for real companies: {query}")

        urls = set()

        try:
            with DDGS() as ddgs:
                results = ddgs.text(
                    query,
                    region="in-en",
                    safesearch="moderate",
                    max_results=num_results * 3,  # search more to filter later
                )

                for r in results:
                    raw_url = r.get("href")
                    if not raw_url:
                        continue

                    if not self.is_valid_company_site(raw_url):
                        continue

                    root = self.clean_domain(raw_url)
                    urls.add(root)

                    if len(urls) >= num_results:
                        break

        except Exception as e:
            print("❌ Search error:", e)

        return list(urls)
