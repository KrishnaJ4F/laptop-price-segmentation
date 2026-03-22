from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd, re, time, random

LISTING_PAGES = 44
MAX_PRODUCTS = 1100
OUT = "laptop.csv"

# ---------------------------------------------------------
#   PRE-COMPILED REGEX (FAST)
# ---------------------------------------------------------
CPU_RX = [
    re.compile(r"(intel core i\d{1,2}\s?\d*\s?(?:[a-z]{1,4})?\s?\(?\d{1,2}(?:th|nd|rd|st)? gen\)?\s?\d*[a-z]{0,4})", re.I),
    re.compile(r"(intel core i\d{1,2}\s?\d{3,4}[a-z]{0,4})", re.I),
    re.compile(r"(intel\s+core\s+ultra\s+\d{1,2}\s*\d{3,4}[a-z]?)", re.I),
    re.compile(r"(intel xeon[\w\s\-]*)", re.I),
    re.compile(r"(intel pentium[\w\s\-]*)", re.I),
    re.compile(r"(intel celeron[\w\s\-]*)", re.I),
    re.compile(r"(amd ryzen \d{1,2}\s?\d{3,5}[a-z]{0,4})", re.I),
    re.compile(r"(amd ryzen threadripper[\w\s\-]*)", re.I),
    re.compile(r"(amd athlon[\w\s\-]*)", re.I),
    re.compile(r"(apple m\d[\w\-]*)", re.I),
    re.compile(r"(snapdragon[\w\s\-]+)", re.I),
    re.compile(r"(qualcomm[\w\s\-]+)", re.I),
    re.compile(r"(mediatek[\w\s\-]+)", re.I),
    re.compile(r"(exynos[\w\d\-\s]+)", re.I)
]

GPU_RX = [
    re.compile(r"(nvidia geforce rtx\s?\d{3,4}(?:[\s\-]?[a-z0-9]{1,12})?)", re.I),
    re.compile(r"(nvidia geforce gtx\s?\d{3,4}(?:[\s\-]?[a-z0-9]{1,12})?)", re.I),
    re.compile(r"(nvidia quadro[\w\d\-]*)", re.I),
    re.compile(r"(nvidia tesla[\w\d\-]*)", re.I),
    re.compile(r"(amd radeon rdna\s?\d)", re.I),
    re.compile(r"(amd radeon[\w\d\s\-]+)", re.I),
    re.compile(r"(intel iris xe)", re.I),
    re.compile(r"(intel uhd graphics)", re.I),
    re.compile(r"(intel hd graphics)", re.I),
    re.compile(r"(intel arc[\w\d\-]*)", re.I),
    re.compile(r"(apple gpu[\w\d]*)", re.I),
    re.compile(r"(adreno[\w\d\-]+)", re.I),
    re.compile(r"(mediatek integrated graphics)", re.I)
]

BRANDS=["hp","dell","lenovo","asus","acer","msi","apple","samsung","lg","infinix","realme","motorola"]
SERIES=["ideapad","thinkpad","vivobook","pavilion","inspiron","victus","omen",
        "aspire","swift","blade","predator","zenbook",
        "macbook","chromebook","yoga","loq"]

# ---------------------------------------------------------
#         UTILS
# ---------------------------------------------------------
def clean(t): return re.sub(r"\s+"," ",t).strip() if t else ""
def num(t):
    if not t: return None
    s = re.sub(r"[^\d]","",t)
    return int(s) if s.isdigit() else None
def enforce(v): return "Not Available" if (not v or str(v).lower() in ("unknown","none","nan")) else v

def pick(soup, arr):
    for a in arr:
        x = soup.select_one(a)
        if x and x.get_text(strip=True):
            return clean(x.get_text(" ",strip=True))
    return None

def p_series(t):
    t=t.lower()
    return next((s for s in SERIES if s in t),None)

def p_cpu(t):
    t=t.lower()
    for r in CPU_RX:
        m=r.search(t)
        if m:
            cpu = clean(m.group())
            cpu = re.sub(r"\s*[-|—|\(].*$","",cpu).strip()
            return cpu

    m=re.search(r"\b(i3|i5|i7|i9|ryzen\s?\d)\b",t,re.I)
    return clean(m.group()) if m else None

# -------------------------------------------------------------------
# ------------------------ ONLY GPU FIX ------------------------------
# -------------------------------------------------------------------
def p_gpu(t):
    t = t.lower()

    for r in GPU_RX:
        m = r.search(t)
        if m:
            gpu = clean(m.group())
            gpu = re.sub(r"\s+", " ", gpu)

            gpu = gpu.replace("nvidia","NVIDIA").replace("geforce","GeForce") \
                     .replace("rtx","RTX").replace("gtx","GTX") \
                     .replace("intel","Intel").replace("iris","Iris") \
                     .replace("uhd","UHD").replace("hd","HD") \
                     .replace("arc","Arc").replace("amd","AMD") \
                     .replace("radeon","Radeon").replace("apple","Apple")

            return gpu.strip()

    m = re.search(r"(rtx|gtx)\s?\d{3,4}(?:\s?(?:ti|max\-q|super|laptop\s?gpu))?", t, re.I)
    if m:
        gpu = m.group().upper()
        return f"NVIDIA GeForce {gpu}"

    m = re.search(r"arc\s?([a-z]?\d{3,4}m?)", t, re.I)
    if m:
        return f"Intel Arc {m.group(1).upper()}"

    return None
# -------------------------------------------------------------------

def p_brand(t):
    t=t.lower()
    return next((b for b in BRANDS if b in t),None)

def p_ram(t):
    m=re.search(r"\b\d{1,2}\s?gb\b",t.lower())
    return clean(m.group()) if m else None

def p_store(t):
    m=re.search(r"\b\d{3,4}\s?gb\b|\b\d{1,2}\s?tb\b",t.lower())
    return clean(m.group()) if m else None

def p_disp(t):
    m=re.search(r"\b\d{1,2}\.?\d?\s?inch\b",t.lower())
    return clean(m.group()) if m else None

def p_w(t):
    m=re.search(r"\b\d\.\d{1,2}\s?kg\b",t.lower())
    return clean(m.group()) if m else None

def p_os(t):
    m=re.search(r"windows\s?\d{1,2}|chrome os|mac os|ubuntu",t.lower())
    return clean(m.group()) if m else None

def p_rev_count(t):
    if not t: return None
    # Expecting "1,234 Ratings & 56 Reviews" or similar
    # We want to extract "56 Reviews" or just "56"
    # Let's extract the number before "Reviews"
    m = re.search(r"([\d,]+)\s?Reviews", t, re.I)
    return m.group(1) if m else None

# ---------------------------------------------------------
#       BEST DRIVER CONFIG FOR VS CODE
# ---------------------------------------------------------
def start():
    o = webdriver.ChromeOptions()

    # FAST & STABLE FOR VS CODE
    o.add_argument("--disable-blink-features=AutomationControlled")
    o.add_argument("--disable-gpu")
    o.add_argument("--no-sandbox")
    o.add_argument("--disable-dev-shm-usage")
    o.add_argument("--start-maximized")
    o.add_argument("--disable-extensions")
    o.add_experimental_option("excludeSwitches", ["enable-automation"])
    o.add_experimental_option('useAutomationExtension', False)

    # HEADLESS MODE WORKS ON VS CODE (NOT JUPYTER)
    o.add_argument("--headless=new")

    d = webdriver.Chrome(options=o)
    d.set_page_load_timeout(35)
    d.set_script_timeout(35)

    return d

# ---------------------------------------------------------
#       SAFE GET (NO MORE TIMEOUT ERROR)
# ---------------------------------------------------------
def get(d, u, retry=3):
    for i in range(retry):
        try:
            d.get(u)
            WebDriverWait(d, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            return True
        except Exception:
            time.sleep(2)
    return False

# ---------------------------------------------------------
#          LISTING SCRAPER (STABLE SCROLLING)
# ---------------------------------------------------------
def listing(d):
    urls=[]; info={}
    sels=["a.CGtC98[href]","a._1fQZEK[href]","a.IRpwTa[href]","a._2kHMtA[href]","a.k7wcnx[href]"]

    for p in range(1, LISTING_PAGES+1):
        u=f"https://www.flipkart.com/search?q=laptops&page={p}"
        if not get(d,u): continue

        time.sleep(1.5)

        # SAFE SCROLLING
        for _ in range(3):
            try:
                d.execute_script("window.scrollBy(0, 700);")
                time.sleep(0.5)
            except:
                time.sleep(1)

        s = BeautifulSoup(d.page_source, "html.parser")

        a=[]
        for sel in sels:
            a.extend(s.select(sel))

        for x in a:
            href = x.get("href")
            if not href or "/p/" not in href: continue

            full = href if href.startswith("http") else "https://www.flipkart.com"+href
            if full in urls: continue

            pnode = x
            for _ in range(4):
                if not pnode: break
                if pnode.select_one("div.KzDlHZ,div._4rR01T,div.RG5Slk"): break
                pnode = pnode.parent

            title = clean(
                pnode.select_one("div.KzDlHZ,div._4rR01T,div.RG5Slk").get_text(" ",strip=True)
            ) if pnode.select_one("div.KzDlHZ,div._4rR01T,div.RG5Slk") else clean(x.get_text(" ",strip=True))

            price = pick(pnode, ["div._30jeq3","div.Nx9bqj","div.hZ3P6w"])
            
            # UPDATED SELECTORS FROM USER CONSOLE LOGS
            original = pick(pnode, ["div.kRYCnD", "div.gxR4EY", "div.QiMO5r div", "div._3I9_wc", "div.yRaY8j"])
            discount = pick(pnode, ["div.HQe8jr span", "div._3Ay6Sb span", "div.UkUFwK span"])
            
            rating = pick(pnode, ["div._3LWZlK","div.XQDdHH","div.MKiFS6"])
            reviews = pick(pnode, ["span._2_R_DZ","span.PvbNMB"])

            li=[clean(i.get_text(" ",strip=True)) for i in pnode.select("ul li")]
            raw = " | ".join(li) if li else None

            urls.append(full)
            info[full] = {
                "Title": title,
                "PriceRaw": price,
                "OriginalRaw": original,
                "Discount": discount,
                "Rating": rating,
                "ReviewsRaw": reviews,
                "SpecsRaw": raw
            }

            if len(urls) >= MAX_PRODUCTS:
                return urls, info

        time.sleep(0.7)

    return urls, info

# ---------------------------------------------------------
#        PRODUCT PAGE SCRAPER
# ---------------------------------------------------------
def prod(d,u):
    if not get(d,u): return {}
    time.sleep(1.2)

    s = BeautifulSoup(d.page_source,"html.parser")
    return {
        "Title": pick(s,["span.B_NuCI","h1"]),
        "Rating": pick(s,["div._3LWZlK","div.XQDdHH"]),
        "ReviewsRaw": pick(s,["span._2_R_DZ"]),
        "PriceRaw": pick(s,["div._30jeq3","div.Nx9bqj"]),
        
        # ALSO UPDATED HERE FOR CONSISTENCY
        "OriginalRaw": pick(s,["div.kRYCnD", "div.gxR4EY", "div._3I9_wc", "div.yRaY8j", "div._25b18c ._3I9_wc"]),
        "Discount": pick(s,["div.HQe8jr span", "div._3Ay6Sb span", "div.UkUFwK span", "div._25b18c ._3Ay6Sb"]),
    }

# ---------------------------------------------------------
#                FINAL MERGE
# ---------------------------------------------------------
def merge(urls,info,data):
    out=[]
    for u in urls:
        p=data.get(u,{})
        l=info.get(u,{})
        title=p.get("Title") or l.get("Title") or ""
        raw=l.get("SpecsRaw") or ""
        m=" ".join([title,raw])

        # Discount Percentage Extraction
        disc_raw = p.get("Discount") or l.get("Discount")
        disc_pct = num(disc_raw) if disc_raw else None # Extract number from "45% off"

        out.append({
            "Title": enforce(title),
            "Brand": enforce(p_brand(title) or p_brand(raw)),
            "Series": enforce(p_series(m)),
            "CPU": enforce(p_cpu(m)),
            "GPU": enforce(p_gpu(m)),
            "RAM": enforce(p_ram(m)),
            "Storage": enforce(p_store(m)),
            "Display": enforce(p_disp(m)),
            "Weight": enforce(p_w(m)),
            "OS": enforce(p_os(m)),
            "Price(Rs)": num(p.get("PriceRaw") or l.get("PriceRaw")),
            "Original Price(Rs)": num(p.get("OriginalRaw") or l.get("OriginalRaw")),
            "Discount Percentage": disc_pct if disc_pct else "Not Available",
            "Rating": enforce(p.get("Rating") or l.get("Rating")),
            "Review Count": enforce(p_rev_count(p.get("ReviewsRaw") or l.get("ReviewsRaw"))),
            "Specs Raw": enforce(raw),
            "Product URL": u
        })
    return out

# ---------------------------------------------------------
#                      MAIN
# ---------------------------------------------------------
def main():
    d=start()
    urls,info=listing(d)

    data={}
    for u in urls:
        # Check if we have GPU info from listing
        l = info.get(u, {})
        title = l.get("Title") or ""
        raw = l.get("SpecsRaw") or ""
        m = " ".join([title, raw])
        gpu_found = p_gpu(m)

        # OPTIMIZATION: If we already have the price AND GPU from listing, skip the slow product page load
        # This makes the scraper ~20x faster, but we need to visit if GPU is missing (likely truncated title)
        if l.get("PriceRaw") and gpu_found:
            print(f"Skipping {u} (Data found in listing)")
            data[u]={} 
        else:
            print(f"Visiting {u} (GPU missing or Data missing)")
            data[u]=prod(d,u)
            time.sleep(random.uniform(0.5,1.0))

    rows=merge(urls,info,data)
    pd.DataFrame(rows).to_csv(OUT,index=False)

    try: d.quit()
    except: pass

    print("Saved:", OUT)

if __name__=="__main__":
    main()
