import os
import time
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, request
import threading

app = Flask(__name__)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SPOTIFY_RESET_URL = "https://accounts.spotify.com/en/password-reset"
VEZSTR_URL = "https://vezstr.com"

# Webhook endpoint
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), None)
    application.process_update(update)
    return 'OK'

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
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 40)
    
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
        time.sleep(3)
        
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
            for (var i = 0; i
