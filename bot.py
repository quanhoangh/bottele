import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="🌐 %(message)s")

# ======================================================
# GLOBALS
# ======================================================
driver = None
task = None
stop_flag = False

# ======================================================
# SELENIUM DRIVER CHO RAILWAY
# ======================================================
def create_driver():
    logging.info("🚀 Khởi tạo driver Chromium (Railway)...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")

    # Railway path
    options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)

    logging.info("✅ Driver đã sẵn sàng.")
    return driver

# ======================================================
# LOGIN
# ======================================================
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver

    if len(context.args) == 0:
        await update.message.reply_text("Nhập dạng: /login CODE")
        return

    code = context.args[0]
    await update.message.reply_text(f"🔑 Đang login với code: {code}")

    try:
        driver = create_driver()
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi tạo driver: {e}")
        return

    driver.get("https://nullzereptool.com/")
    await asyncio.sleep(3)

    try:
        driver.find_element(By.ID, "code").send_keys(code)
    except:
        await update.message.reply_text("❌ Không tìm thấy ô nhập CODE.")
        return

    await asyncio.sleep(1)

    try:
        btn = driver.find_element(By.XPATH, "//button[contains(text(),'Get My Dragon City Information')]")
        driver.execute_script("arguments[0].click();", btn)
    except:
        await update.message.reply_text("❌ Không tìm thấy nút Login.")
        return

    await asyncio.sleep(10)

    # Đóng modal
    try:
        driver.execute_script("document.getElementById('newsModalClose')?.click();")
    except:
        pass

    # Mở tab resources
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[data-tab='resources']")
        driver.execute_script("arguments[0].click();", btn)
    except:
        pass

    await update.message.reply_text("✅ Đăng nhập thành công!")

# ======================================================
# AUTO CLAIM — Bản không TimeOut
# ======================================================
async def auto_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, driver

    while not stop_flag:
        try:
            # Mở lại tab Resources
            try:
                tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-tab='resources']"))
                )
                driver.execute_script("arguments[0].click();", tab)
            except Exception as e:
                logging.info(f"⚠ Không mở được tab resources: {e}")

            await asyncio.sleep(1)

            # Đóng modal nếu có
            try:
                driver.execute_script("document.getElementById('newsModalClose')?.click();")
            except:
                pass

            # Scroll mạnh
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(1)

            # Kiểm tra nút xuất hiện
            claim_btn = WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.ID, "claim-gold-xp"))
            )

            # Đợi click được
            claim_btn = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.ID, "claim-gold-xp"))
            )

            # Scroll chuẩn vào nút
            driver.execute_script("arguments[0].scrollIntoView(true);", claim_btn)
            await asyncio.sleep(0.3)

            # Click
            driver.execute_script("arguments[0].click();", claim_btn)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💰 Claim thành công!"
            )

        except Exception as e:
            logging.info(f"⚠ Claim lỗi: {e}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠ Lỗi claim (retry): {e}"
            )

        await asyncio.sleep(5)

# ======================================================
# START AUTO CLAIM
# ======================================================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global task, stop_flag

    if driver is None:
        await update.message.reply_text("❌ Chưa login. Dùng /login trước.")
        return

    if task is not None and not task.done():
        await update.message.reply_text("⚠ Auto claim đang chạy.")
        return

    stop_flag = False
    task = asyncio.create_task(auto_claim(update, context))
    await update.message.reply_text("▶️ Bắt đầu auto claim.")

# ======================================================
# STOP
# ======================================================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag
    stop_flag = True
    await update.message.reply_text("🛑 Đã tắt auto claim.")

# ======================================================
# OUT
# ======================================================
async def out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver, stop_flag
    stop_flag = True

    if driver:
        driver.quit()
        driver = None

    await update.message.reply_text("🚪 Đã đóng trình duyệt.")

# ======================================================
# CHECK USER INFO
# ======================================================
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver

    if driver is None:
        await update.message.reply_text("❌ Chưa login.")
        return

    await update.message.reply_text("🔄 Đang lấy thông tin...")

    driver.refresh()
    await asyncio.sleep(5)

    try:
        grid = driver.find_element(By.CSS_SELECTOR, "div.grid.grid-cols-2")
        items = grid.find_elements(By.TAG_NAME, "div")

        data = {}
        for i in items:
            txt = i.text.strip()
            if ":" in txt:
                k, v = txt.split(":", 1)
                data[k.strip()] = v.strip()

        msg = (
            "👤 **User Info:**\n"
            f"• Name: {data.get('Name', '?')}\n"
            f"• Gems: {data.get('Gems', '?')}\n"
            f"• Gold: {data.get('Gold', '?')}\n"
            f"• Food: {data.get('Food', '?')}\n"
            f"• XP: {data.get('XP', '?')}\n"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi đọc info: {e}")

# ======================================================
# RUN BOT
# ======================================================
TOKEN = "8029102657:AAF536W2Fh0ihZdCIC92dDAAWHqpwqPrVXo"

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("out", out))
app.add_handler(CommandHandler("check", check))

app.run_polling()
