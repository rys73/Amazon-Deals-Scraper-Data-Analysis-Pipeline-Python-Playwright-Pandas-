import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = r"C:\Users\ighik\OneDrive\Escritorio\html\PORTFOLIO_LINKEDIN\PORTOFOLIO_2_1\WEB_SCRAPING_PROJET_2_\CSV\deals_amazon.csv"
OUTPUT_DIR = r"C:\Users\ighik\OneDrive\Escritorio\html\PORTFOLIO_LINKEDIN\PORTOFOLIO_2_1\PANDAS_PROJET_1_\PDF\\"

# 1 -> CHARGER LES DONNÉES
df = pd.read_csv(CSV_PATH, header=None, names=["ASIN","Name","Price","Old_Price","Discount","URL"])

# 2 -> NETTOYAGE DES CARACTÈRES NON STANDARDS
def clean_text(x):
    if pd.isna(x):
        return ""
    # On supprime les caractères non standards "(CORRECTION d'un warning affiché dans le terminal)"
    return (str(x)
            .replace("\u3001", ",") # virgule Japonaise
            .replace("\uff0c", "") # virgule Chinoise
            .replace("\u2013", "")) # tiret long
df["Name"] = df["Name"].apply(clean_text)

# 3 -> NETTOYAGE DES DONNÉES
def clean_price(x):
    if pd.isna(x) or x == "":
        return 0.0
    x = str(x).replace("Deal Price:", "").replace("EUR", "").replace("\xa0", "").strip()
    try:
        return float(x)
    except:
        return 0.0
df["Price"] = df["Price"].apply(clean_price)
df["Old_Price"] = df["Old_Price"].apply(clean_price)

# 4 -> NETTOYAGE DES RÉDUCTIONS
def clean_discount(x):
    if pd.isna(x) or x == "":
        return 0.0
    x = str(x).replace("% off", "").replace(",", ".").strip()
    try:
        return float(x)
    except:
        return 0.0

df["Discount"] = df["Discount"].apply(clean_discount)
df["Savings"] = df["Old_Price"] - df["Price"] # Calcul de l'économie


# 5 -> CRÉATION DES GRAPHIQUES EN PDF

  # 5.1 -> Répartition des réductions
bins = [0, 10, 20, 30, 40, 50, 100]
labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"]
df["Discount_Bin"] = pd.cut(df["Discount"], bins=bins, labels=labels, right=False)
discount_counts = df["Discount_Bin"].value_counts().reindex(labels)

plt.figure(figsize=(8,5))
discount_counts.plot(kind="bar", color="skyblue")
plt.title("Répartition des réductions (%)")
plt.ylabel("Nombre de Produits")
plt.xlabel("Tranches de réduction")
plt.grid(axis="y", linestyle="-", alpha=0.5)
plt.tight_layout()
plt.savefig(OUTPUT_DIR + "amazon_tranche_de_reduction.pdf")   
plt.close()


  # 3.2 -> Top 10 économies (€)
top_savings = df[df["Savings"] > 0].sort_values("Savings",ascending=False).head(10)
plt.figure(figsize=(14,7))
plt.barh(top_savings["Name"], top_savings["Savings"], color="green")
plt.title("Top 10 meilleures économies (€)")
plt.xlabel("Économie (€)")
plt.ylabel("Produit")
plt.gca().invert_yaxis()
for i, v in enumerate(top_savings["Savings"]):
    plt.text(v + 0.5, i, f"{v:.2f}€", va="center")
# On ajuste la marge gauche pour laisser de la place aux noms des produits
plt.subplots_adjust(left=0.35)
plt.savefig(OUTPUT_DIR + "amazon_top_10_meilleures_economies.pdf")
plt.close()


  # 3.3 -> Prix moyen avant / après
avg_old = df[df["Old_Price"] > 0]["Old_Price"].mean()
avg_new = df["Price"].mean()
plt.figure(figsize=(6,5))
plt.bar(["Avant promo", "Après promo"], [avg_old, avg_new], color=["blue", "orange"])
plt.title("Prix moyen avant/après")
plt.ylabel("Prix (€)")
for i, v in enumerate([avg_old, avg_new]):
    plt.text(i, v + 1, f"{v:.2f}€", ha="center")
plt.tight_layout()
plt.savefig(OUTPUT_DIR + "amazon_prix_moyen_avant_et_apres.pdf")
plt.close()


  # 3.4 -> Répartition des prix actuels
bins_price = [0, 20, 50, 100, 500, 1000]
labels_price = ["<20€", "20-50€", "50-100€", "100-500€", "500€+"]
df["Price_Bin"] = pd.cut(df["Price"], bins=bins_price, labels=labels_price, right=False)
price_counts = df["Price_Bin"].value_counts().reindex(labels_price)
plt.figure(figsize=(8,5))
price_counts.plot(kind="bar", color="coral")
plt.title("Répartition des prix actuels")
plt.xlabel("Tranches de prix")
plt.ylabel("Nombre de produits")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(OUTPUT_DIR + "amazon_repartition_des_prix_actuels.pdf")
plt.close()


  # 3.5 -> Économie moyenne par tranche de prix
# On garde uniquement les produits avec une vraie réduction
df_savings = df[df["Savings"] > 0].copy()
bins_price = [0, 20, 50, 100, 1000]
labels_price = ["<20€", "20-50€", "50-100€", "100€+"]
df_savings["Price_Bin"] = pd.cut(df_savings["Price"], bins=bins_price, labels=labels_price, right=False)
    
# On calcule l'économie moyenne par tranche
avg_savings = df_savings.groupby("Price_Bin", observed=False)["Savings"].mean().reindex(labels_price)
plt.figure(figsize=(8,5))
avg_savings.plot(kind="bar", color="purple")
plt.title("Économie moyenne (€) par tranche de prix")
plt.xlabel("Tranches de prix actuels")
plt.ylabel("Économie moyenne (€)")
plt.grid(axis="y", linestyle="--", alpha=0.5)

# On affichage des valeurs au-dessus des barres
for i, v in enumerate(avg_savings):
    if pd.notna(v):
        plt.text(i, v + 0.5, f"{v:.2f}€", ha="center")
plt.tight_layout()
plt.savefig(OUTPUT_DIR + "amazon_economie_par_tranche_de_prix.pdf")
plt.close()


print("Tous les graphiques ont été générés en PDF séparés")


