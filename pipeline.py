import os
import json
import csv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
from openai import OpenAI

ASPECT_RATIOS = {
    "1_1": ("1024x1024", (1080, 1080)),     
    "9_16": ("1024x1536", (1080, 1920)),    
    "16_9": ("1536x1024", (1920, 1080))     
}

INPUT_ASSETS = "assets/input"
OUTPUT_DIR = "outputs"
LOG_FILE = "outputs/pipeline_log.csv"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

## Gaurdrails
PROHIBITED_WORDS = ["PII","Profanity", "gauranteed", "forever free"]

# Example brand colors (RGB tuples)
REQUIRED_COLORS = [(0, 51, 102)] 

# ----------------- Helper fuunctions -----------------
def load_campaign_brief(path="brief.json"):
    with open(path, "r") as f:
        return json.load(f)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_with_openai(product, aspect_ratio, message):
    api_size, final_size = ASPECT_RATIOS[aspect_ratio]
    prompt = f"High quality marketing image of {product}. Campaign message: {message}"
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=api_size
    )
    image_url = response.data[0].url
    img = Image.open(requests.get(image_url, stream=True).raw)
    img = img.resize(final_size)  
    return img

def overlay_text(image, text):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    draw.text((50, 50), text, font=font, fill="white")
    return image

def add_logo(image, logo_path="assets/input/logo.png"):
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((100, 100))
        image.paste(logo, (image.width - 120, image.height - 120), logo)
    return image

def check_brand_colors(image, required_colors=REQUIRED_COLORS):
    colors = image.getcolors(maxcolors=1000000)
    if not colors:
        return False
    most_common = sorted(colors, key=lambda x: -x[0])[0][1]
    return any(
        all(abs(most_common[i] - rc[i]) < 50 for i in range(3))
        for rc in required_colors
    )

def check_legal_message(message):
    for word in PROHIBITED_WORDS:
        if word.lower() in message.lower():
            return False, word
    return True, None

def log_result(campaign, product, ratio, status, notes=""):
    ensure_dir("outputs")
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "campaign", "product", "ratio", "status", "notes"])
        writer.writerow([datetime.utcnow(), campaign, product, ratio, status, notes])

# ----------------- Pipeline -----------------
def process_campaign(brief):
    campaign_name = brief["campaign_name"].replace(" ", "_")

    # Check legal compliance before generating
    legal_ok, bad_word = check_legal_message(brief["message"])
    if not legal_ok:
        print(f"❌ Legal check failed: contains prohibited word '{bad_word}'")
        log_result(campaign_name, "ALL", "N/A", "FAIL", f"Prohibited word: {bad_word}")
        return

    for product in brief["products"]:
        for ratio_name, size in ASPECT_RATIOS.items():
            output_path = os.path.join(OUTPUT_DIR, campaign_name, product, ratio_name)
            ensure_dir(output_path)

            asset_path = os.path.join(INPUT_ASSETS, f"{product}.jpg")
            try:
                if os.path.exists(asset_path):
                    img = Image.open(asset_path).resize(size)
                else:
                    img = generate_with_openai(product, ratio_name, brief["message"])

                img = overlay_text(img, brief["message"])
                img = add_logo(img)

                if not check_brand_colors(img):
                    log_result(campaign_name, product, ratio_name, "FAIL", "Brand color missing")
                    print(f"⚠️ Brand color check failed for {product} ({ratio_name})")
                    continue

                out_file = os.path.join(output_path, f"{product}_{ratio_name}.jpg")
                img.save(out_file)
                log_result(campaign_name, product, ratio_name, "PASS", "Generated successfully")
                print(f"✅ Generated: {out_file}")

            except Exception as e:
                log_result(campaign_name, product, ratio_name, "ERROR", str(e))
                print(f"❌ Error generating {product} ({ratio_name}): {e}")

if __name__ == "__main__":
    brief = load_campaign_brief()
    process_campaign(brief)
