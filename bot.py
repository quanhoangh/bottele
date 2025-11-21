import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# ==========================
# Biến toàn cục
# ==========================
driver = None
task = None
stop_flag = False

# ==========================
# /login CODE
# ==========================
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver
    if len(context.args) == 0:
        await update.message.reply_text("Nhập code dạng: /login CODE")
        return

    code = context.args[0]

    await update.message.reply_text(f"🔑 Đang login với code: {code} ...")

    # --- Selenium setup ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://nullzereptool.com/")
    await asyncio.sleep(2)

    # Nhập code
    input_box = driver.find_element(By.ID, "code")
    input_box.send_keys(code)
    await asyncio.sleep(1)

    # Click nút login
    button = driver.find_element(By.XPATH, "//button[contains(text(),'Get My Dragon City Information')]")
    button.click()
    await asyncio.sleep(10)  # chờ load
    # Ẩn modal news
    try:
        close_btn = driver.find_element(By.ID, "newsModalClose")
        close_btn.click()
        await asyncio.sleep(2)
        button_extra = driver.find_element(By.CSS_SELECTOR, "button[data-tab='resources']")
        button_extra.click()
        await asyncio.sleep(1)
    except:
        pass

    await update.message.reply_text("✅ Login xong. Sẵn sàng dùng /stats để claim.")

# ==========================
# Hàm auto claim
# ==========================
async def auto_claim(update: Update):
    global stop_flag, driver
    while not stop_flag:
        try:
            button_claim = driver.find_element(By.XPATH, "//button[@id='claim-gold-xp']")
            button_claim.click()
            await update.message.reply_text("💰 Claim thành công!")
        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi claim: {e}")
        await asyncio.sleep(5)  # mỗi 5 giây claim 1 lần

# ==========================
# /stats → start auto claim
# ==========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global task, stop_flag
    if driver is None:
        await update.message.reply_text("❌ Chưa login. Dùng /login CODE trước.")
        return

    if task is not None and not task.done():
        await update.message.reply_text("⚠️ Bot đang chạy claim.")
        return

    await update.message.reply_text("▶️ Bắt đầu auto claim Gold & XP ...")
    stop_flag = False
    # chạy task riêng cho claim
    task = asyncio.create_task(auto_claim(update))

# ==========================
# /stop → dừng claim
# ==========================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, task
    if task is None or task.done():
        await update.message.reply_text("❗ Bot chưa chạy claim.")
        return
    stop_flag = True
    await update.message.reply_text("🛑 Đã nhận lệnh /stop. Auto claim dừng.")
    task = None

# ==========================
# /out → đóng Selenium
# ==========================
async def out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver, task, stop_flag
    stop_flag = True
    if driver:
        driver.quit()
        driver = None
    await update.message.reply_text("🚪 Trình duyệt đã đóng, bot tắt Selenium.")

# ==========================
# Khởi chạy bot
# ==========================
TOKEN = "8029102657:AAF536W2Fh0ihZdCIC92dDAAWHqpwqPrVXo"
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("out", out))

app.run_polling()
