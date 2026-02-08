import asyncio, csv, logging
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

AMAZON_URL = "https://www.amazon.com"
CSV_PATH = r"C:\Users\ighik\OneDrive\Escritorio\html\PORTFOLIO_LINKEDIN\PORTOFOLIO_2_1\WEB_SCRAPING_PROJET_2_\CSV\deals_amazon.csv"

""""
Script de scraping automatisé des promotions Amazon ("Today's Deals")
Utilisation de Playwright (navigation dynamique) + BeautifulSoup (parsing HTML)
Export des données en CSV prêt pour une analyse ou une automatisation business.
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BATCH_SIZE = 5      # Limite volontaire pour contrôler la charge et éviter les blocages Amazon
SCROLL_PAUSE = 1.0  # Pause stratégique pour synchroniser le chargement dynamique (JS)

async def go_to_deals(page):
    # Navigation automatisée vers la page de promotions Amazon
    # avec gestion des popups bloquantes (UX réelle)
    deals_link = page.locator("div#nav-main a", has_text="Today's Deals")

    # Gestion anticipative des popups pour garantir une navigation stable
    dismiss = page.locator('input[data-action-type="DISMISS"]')
    if await dismiss.count() > 0:
        await dismiss.click()
        await page.wait_for_timeout(500) # Petite pause pour stabiliser le DOM
    
    # Navigation vers la page de "Today's Deals"
    await deals_link.click()

    # On attend qu'au moins un deal soit chargé
    await page.wait_for_selector('[data-test-index="0"]')



async def collect_visible_deals(page, seen_asins):
    # Extraction intelligente des deals visibles à l'écran
    # (scraping progressif pour éviter les doublons et la surcharge)
    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # Parcours des cartes produits actuellement chargées dans le DOM
    for card in soup.select('[data-testid="product-card"]'):
        asin = card.get('data-asin', '')
        # Si l'ASIN est manquant ou déjà collecté, on ignore (anti-duplication)
        if not asin or asin in seen_asins:
            continue
        # Nom du produit
        name_tag = card.select_one('.a-truncate-full')
        name = name_tag.text.strip() if name_tag else ''
        # Prix actuel
        price_tag = card.select_one('.a-price .a-offscreen')
        price = price_tag.text.strip() if price_tag else ''
        # Ancien prix (elle peut être "List" ou "Was" selon la promo)
        old_price_tag = card.select_one('span.a-offscreen:contains("List")') or \
                card.select_one('span.a-offscreen:contains("Was")')
        old_price = old_price_tag.text.replace("List:", "").replace("Was:", "").strip() if old_price_tag else ""
        # Badge de réduction (% OFF)
        discount_tag = card.select_one('.style_filledRoundedBadgeLabel__Vo-4g')
        discount = discount_tag.text.strip() if discount_tag else ''
        # Lien vers la fiche produit
        # urljoin garantit une URL complète même si Amazon fournir un chemin relatif
        link_tag = card.select_one('[data-testid="product-card-link"]')
        url = urljoin(AMAZON_URL, link_tag['href']) if link_tag else ''

        results.append({"ASIN": asin, "Name": name, "Price": price, "Old_Price": old_price, "Discount": discount, "URL": url})
        # On mémorise l'ASIN pour éviter toute duplication future
        seen_asins.add(asin)
        # On limite volontairement la collect par Batch
        if len(results) >= BATCH_SIZE:
            break 
    return results

async def main():
   # Création d'un CSV structuré compatible Excel / Pandas / BI tools
    csv_file = open(CSV_PATH, "w", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(csv_file, fieldnames=["ASIN", "Name", "Price", "Old_Price", "Discount", "URL"])
    writer.writeheader()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        # User-Agent pour réduire le risque de blocage
        context = await browser.new_context(user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"))
        page = await context.new_page()
        await page.goto(AMAZON_URL)
        await page.wait_for_load_state("domcontentloaded")
        # Accès à la page des promotions
        await go_to_deals(page)

        seen_asins = set()
        # Boucle de scraping progressive avec sauvegarde continue
        # (endurant aux crashs et interruptions)
        while True:
            # On collecte uniquement, que ce qui est actuellement visible
            batch = await collect_visible_deals(page, seen_asins)
            if not batch:
                break
            # S'il y a aucun nouveau alors sa met fin au scraping
            for row in batch:
                writer.writerow(row)
            # Sauvegarde immédiate pour éviter toute perte de données en cas de CRASH
            csv_file.flush()
            logging.info(f"{len(batch)} deals ajoutés. Total: {len(seen_asins)}")

            # Scroll progressif (Amazon charge dynamiquement (JS))
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(SCROLL_PAUSE)
            # Bouton "View more deals" il est parfois présent
            load_more_btn = page.locator('button:has-text("View more deals")')

            if await load_more_btn.is_visible() and await load_more_btn.is_enabled():
                logging.info("View more deals...")
                await load_more_btn.click()
                await page.wait_for_selector('[data-testid="product-card"]')
            else:
                # Si le bouton n'existe pas, on continue simplement le scroll
                # On fais une dernière vérification avant de continuer la boucle 
                if not await load_more_btn.count():
                   logging.info("Aucun bouton 'View more deals'")
                   continue

        await context.close()
        await browser.close()
        csv_file.close()
        logging.info("Scraping terminé !")

if __name__ == "__main__":
    asyncio.run(main())
