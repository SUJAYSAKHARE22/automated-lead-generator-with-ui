import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
import re

def extract_emails(text):
    """Extract email addresses from text"""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return list(set(emails))

def extract_phones(text):
    """Extract phone numbers from text"""
    phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
    return list(set(phones))

def extract_team_members(soup, full_text):
    """Extract team members and executives more accurately"""
    team = {}
    
    # Define positions to look for with different patterns
    positions = {
        'CEO': ['Chief Executive Officer', 'CEO'],
        'CTO': ['Chief Technology Officer', 'CTO'],
        'CFO': ['Chief Financial Officer', 'CFO'],
        'COO': ['Chief Operating Officer', 'COO'],
        'CMO': ['Chief Marketing Officer', 'CMO'],
        'Founder': ['Founder', 'Co-Founder', 'Co Founder'],
        'President': ['President'],
        'Director': ['Director'],
        'Manager': ['Manager'],
        'Head': ['Head of', 'Head'],
    }
    
    found_members = False
    
    # Search for team members with explicit patterns
    for position, variations in positions.items():
        members_list = []
        
        for variation in variations:
            # Multiple patterns to match names with positions
            patterns = [
                rf'{variation}[:\s\-]+([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # Position: Name
                rf'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)[,\s]+(?:is\s+)?{variation}',  # Name, Position
                rf'{variation}[:\s]+([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)[,\-\s]',  # Position: Name,
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    clean_name = match.strip() if isinstance(match, str) else match[0].strip() if match else ""
                    # Filter out common false positives
                    if clean_name and len(clean_name.split()) >= 2 and len(clean_name) < 50:
                        if not any(x in clean_name.lower() for x in ['click', 'read', 'download', 'learn', 'explore', 'discover']):
                            if clean_name not in members_list:
                                members_list.append(clean_name)
                                found_members = True
        
        if members_list:
            team[position] = members_list[:3]  # Limit to 3 per position
    
    # Also search for "About Us" or "Team" sections
    about_section = soup.find(['div', 'section'], class_=re.compile('about|team|leadership|staff', re.I))
    if about_section:
        # Look for patterns with names and titles in this section
        section_text = about_section.get_text()
        
        # Try to extract structured data from team section
        for position, variations in positions.items():
            if position not in team:
                for variation in variations:
                    pattern = rf'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+[-–]\s+{variation}'
                    matches = re.findall(pattern, section_text, re.IGNORECASE)
                    if matches:
                        team[position] = [m.strip() for m in matches if m.strip()][:3]
                        found_members = True
    
    return team, found_members

def extract_services(soup, full_text):
    """Extract services and products"""
    services = []
    
    # Look for service descriptions in common sections
    service_keywords = ['service', 'product', 'solution', 'offering', 'feature', 'capability']
    
    for keyword in service_keywords:
        # Find sections with service keywords
        sections = soup.find_all(['div', 'section', 'li'], class_=re.compile(keyword, re.I))
        for section in sections:
            text = section.get_text(strip=True)
            if len(text) > 20 and len(text) < 500:  # Reasonable length
                if text not in services:
                    services.append(text)
    
    # Also extract from paragraphs near service-related words
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if any(kw in text.lower() for kw in service_keywords) and len(text) > 50 and len(text) < 500:
            if text not in services:
                services.append(text)
    
    return services[:10]  # Limit to 10 services

def extract_company_info(soup, url):
    """Extract basic company information"""
    info = {}
    
    # Company name
    title = soup.title.string if soup.title else ""
    info['Name'] = title.split('|')[0].strip() if '|' in title else title.strip()
    
    # Description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        info['Description'] = meta.get("content", "").strip()
    
    return info

def scrape_website(url):
    print(f"Scraping website: {url}")

    # Browser-like header
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Send request to website
    try:
        response = requests.get(url, headers=headers, timeout=15)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return

    # Check if request succeeded
    if response.status_code != 200:
        print(f"Failed to fetch website. Status: {response.status_code}")
        return

    # Parse HTML
    soup = BeautifulSoup(response.text, "lxml")

    # Extract domain name
    domain = urlparse(url).netloc.replace("www.", "")

    # Create data folders
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Save HTML file
    html_path = f"data/raw/{domain}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print(f"✓ HTML saved: {html_path}")

    # Get full text
    for tag in soup(["script", "style"]):
        tag.decompose()
    full_text = soup.get_text()

    # Extract information
    company_info = extract_company_info(soup, url)
    services = extract_services(soup, full_text)
    team, team_found = extract_team_members(soup, full_text)
    emails = extract_emails(full_text)
    phones = extract_phones(full_text)

    # Save as structured text file
    text_path = f"data/processed/{domain}.txt"
    with open(text_path, "w", encoding="utf-8") as f:
        # Header
        f.write("\n")
        f.write("┌" + "─"*78 + "┐\n")
        f.write(f"│ COMPANY INFORMATION: {domain.upper():<52}│\n")
        f.write("└" + "─"*78 + "┘\n\n")
        
        # Company Details
        f.write("📋 COMPANY DETAILS\n")
        f.write("-"*80 + "\n")
        
        if company_info.get('Name'):
            f.write(f"  Company Name: {company_info['Name']}\n")
        f.write(f"  Website: {url}\n")
        
        if company_info.get('Description'):
            f.write(f"  Description:\n")
            f.write(f"    {company_info['Description']}\n")
        f.write("\n")

        # Services & Products
        if services:
            f.write("🎯 SERVICES & PRODUCTS\n")
            f.write("-"*80 + "\n")
            for i, service in enumerate(services, 1):
                # Clean and format service description
                clean_service = service.replace('\n', ' ').strip()
                f.write(f"  {i}. {clean_service}\n\n")
            f.write("\n")

        # Team & Leadership
        f.write("👥 TEAM & LEADERSHIP\n")
        f.write("-"*80 + "\n")
        
        # Define all positions to check
        positions_to_show = ['CEO', 'CTO', 'CFO', 'COO', 'CMO', 'Founder', 'President', 'Director', 'Manager', 'Head']
        
        if team:
            for position in positions_to_show:
                if position in team:
                    f.write(f"  {position}:\n")
                    for name in team[position]:
                        f.write(f"    • {name}\n")
                else:
                    f.write(f"  {position}: Not mentioned\n")
        else:
            for position in positions_to_show:
                f.write(f"  {position}: Not mentioned\n")
        
        f.write("\n")

        # Contact Information
        if emails or phones:
            f.write("📞 CONTACT INFORMATION\n")
            f.write("-"*80 + "\n")
            if emails:
                f.write(f"  Email Addresses:\n")
                for email in emails[:5]:  # Limit to 5
                    f.write(f"    • {email}\n")
            if phones:
                f.write(f"  Phone Numbers:\n")
                for phone in phones[:5]:  # Limit to 5
                    f.write(f"    • {phone}\n")
            f.write("\n")

        # Footer
        f.write("="*80 + "\n")
        f.write(f"Source: {url}\n")
        f.write("="*80 + "\n")
    
    print(f"✓ Business info extracted: {text_path}\n")
