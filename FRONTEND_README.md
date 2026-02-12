# Lead Scraper Frontend

A beautiful web-based dashboard to view and manage all scraped company leads.

## Features

✨ **Dashboard View**
- See all scraped companies at a glance
- Search and filter companies by name or website
- Quick statistics on emails, phones, and services found
- At-a-glance badges showing data availability

🔍 **Detailed Company View**
- Complete company information (website, description)
- Services and products offered
- Team members and leadership information
- Contact details (emails and phone numbers)
- One-click copy buttons for contact information
- Statistics about each company

📊 **Data Management**
- Export all company data as JSON via `/export` endpoint
- REST API endpoints for programmatic access
- Organized, structured data display

## Installation

### 1. Install Flask

Open a terminal in the `lead_scraper` directory and install Flask:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask

pip install ddgs beautifulsoup4 requests

pip install sentence-transformers torch 
```

## Running the Frontend

1. Make sure you have scraped some company data (run your scraper first)
2. Navigate to the project directory:
   ```bash
   cd c:\Users\Faizan\Desktop\lead_scraper
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
4. Open your browser and go to:
   ```
   http://localhost:5000
   ```

## Available Pages

- **Dashboard**: `http://localhost:5000/` - View all companies
- **Company Detail**: `http://localhost:5000/company/<company-name>` - View details for a specific company
- **API Endpoints**:
  - `http://localhost:5000/api/companies` - Get all companies as JSON
  - `http://localhost:5000/api/companies/<company-name>` - Get company details as JSON
  - `http://localhost:5000/export` - Export all data with metadata

## Features

### Dashboard
- Grid display of all companies
- Search functionality for finding companies
- Visual indicators for available data (emails, phones, team info)
- Quick preview of company information
- One-click access to detailed views

### Company Detail Page
- Complete company information
- Multiple sections: Details, Services, Team, Contact
- Copy-to-clipboard buttons for emails and phones
- Statistics about collected data
- Raw data viewer for debugging
- Direct links to company websites

## File Structure

```
lead_scraper/
├── app.py                    # Main Flask application
├── templates/
│   ├── base.html            # Base template with styling
│   ├── index.html           # Dashboard page
│   └── company_detail.html  # Company detail page
├── data/
│   └── processed/           # Your scraped data files
└── requirements.txt         # Python dependencies
```

## Customization

### Styling
All styles are in the template files. Modify the `<style>` sections in the templates to customize colors, fonts, and layout.

### Data Fields
The parser in `app.py` extracts:
- Company name and website
- Description
- Services/products
- Team members
- Emails and phone numbers

Modify the `parse_company_data()` function to extract additional information.

## Notes

- Make sure your scraped data is in `data/processed/` directory as `.txt` files
- The frontend automatically parses the structured text files
- File names become company names (e.g., `autowisdom.in.txt` → `Autowisdom.in`)
- The application runs in debug mode on port 5000

## Troubleshooting

### No companies showing up?
- Make sure your scraper has generated `.txt` files in `data/processed/`
- Check that the data format matches the expected structure

### Port 5000 already in use?
- Modify the port in `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Change to a different port
  ```

### Python/Flask not found?
- Make sure you installed Flask: `pip install Flask`
- Make sure you're using the correct Python version: `python --version`

## Future Enhancements

Some ideas for improvement:
- Database integration for persistent storage
- Advanced filtering and sorting
- Data export to CSV/Excel
- Bulk contact actions
- Email/SMS campaign integration
- Analytics and insights
- User authentication
- Data validation and cleaning UI

---

Happy lead hunting! 🚀
