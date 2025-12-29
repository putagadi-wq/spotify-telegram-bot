import os
import time
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_RESET_URL = "https://accounts.spotify.com/en/password-reset"
VEZSTR_URL = "https://vezstr.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Spotify Password Reset Bot</b>\n\nKirim username (contoh: <code>testing12345</code>)",
        parse_mode='HTML'
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    status_msg = await update.message.reply_text("⏳ Proses reset Spotify...")
    
    try:
        email_address = f"{username}@vezstr.com"
        link = await run_spotify_reset(email_address)
        await status_msg.edit_text(f"✅ <b>Link Reset:</b>\n<code>{link}</code>", parse_mode='HTML')
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def run_spotify_reset(email_address):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 30)
    
    try:
        driver.get(SPOTIFY_RESET_URL)
        email_input = wait.until(EC.element_to_be_clickable((By.ID, "email_or_username")))
        email_input.clear()
        email_input.send_keys(email_address)
        time.sleep(1)
        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send link')]")))
        send_btn.click()
        
        driver.execute_script("window.open('about:blank', '_blank');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(VEZSTR_URL)
        time.sleep(2)
        
        new_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'text-xs') and contains(@class, 'pt-5') and normalize-space(.)='New']")))
        new_btn.click()
        time.sleep(1)
        
        username_only = email_address.split("@")[0]
        username_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder,'username')]")))
        username_field.clear()
        username_field.send_keys(username_only)
        time.sleep(0.5)
        
        select_domain = wait.until(EC.element_to_be_clickable((By.ID, "domain")))
        select_domain.click()
        time.sleep(1)
        
        driver.execute_script("""
            var elements = document.evaluate("//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'vezstr.com')]", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            for (var i = 0; i < elements.snapshotLength; i++) {
                var el = elements.snapshotItem(i);
                if (el.offsetParent !== null) { el.click(); break; }
            }
        """)
        time.sleep(1)
        
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create")))
        create_btn.click()
        time.sleep(11)
        
        try:
            driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
        except: pass
        
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/password-reset/complete') and contains(@href, 'flow_id=')]")
        reset_link = links[0].get_attribute("href") if links else None
        
        if not reset_link:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for a in all_links:
                href = a.get_attribute("href")
                if href and "spotify.com" in href and "flow_id=" in href:
                    reset_link = href
                    break
        
        if not reset_link:
            raise Exception("Link Spotify tidak ditemukan!")
        
        return reset_link
        
    finally:
        driver.quit()

def main():
    # FIXED VERSION v20.7
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    
    print("🤖 Bot berjalan di Render!")
    application.run_polling()

if __name__ == "__main__":
    main()
