# Amazon Deals – Web Scraping & Data Analysis Project

## Project Overview
This project is an **end-to-end data pipeline** that automatically collects Amazon "Today's Deals", cleans and structures the data, and generates **business-oriented visual insights**.

It demonstrates real-world skills in:
- Web scraping of dynamic websites
- Data cleaning and transformation
- Exploratory data analysis
- Data visualization and reporting
---

## Technologies Used
- **Python 3**
- **Playwright (Async)** – dynamic web scraping
- **BeautifulSoup** – HTML parsing
- **Pandas** – data cleaning & analysis
- **Matplotlib** – data visualization
- **CSV / PDF export**
---

## Part 1 – Web Scraping
The scraper:
- Navigates dynamically through Amazon "Today's Deals"
- Handles infinite scrolling and dynamic loading
- Avoids duplicates using ASIN tracking
- Extracts:
  - Product name
  - Current price
  - Old price
  - Discount percentage
  - Product URL
- Saves data incrementally into a CSV file to prevent data loss
📁 Output: `deals_amazon.csv`
---

##  Part 2 – Data Analysis & Visualization
Using Pandas, the project:
- Cleans and normalizes text, prices, and discounts
- Computes key KPIs such as real savings (€)
- Generates multiple analytical insights:
  - Distribution of discounts
  - Top 10 best deals by savings
  - Average price before vs after promotions
  - Price range distribution
  - Average savings by price category
📁 Outputs: Individual **PDF reports** ready for presentation or business use.
---

##  Business Value
This project simulates a real-world use case:
- Market monitoring
- Promotion analysis
- E-commerce deal optimization
- Automated reporting for decision-making
---

## How to Run
```bash
pip install playwright pandas matplotlib beautifulsoup4
playwright install
python scraper_amazon.py
python analysis_pandas.py
