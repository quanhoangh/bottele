import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================
# Global variables
# ==========================
driver = None
task = None
stop_flag = False

# ==========================
# Selenium driver (Docker)
# ==========================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/chromium"

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)

# ==========================
# /login
# ==========================
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver

    if len(context.args) == 0:
        await update.message.reply_text("Nhập code dạng: /login CODE")
        return

    code = context.args[0]
    await update.message.reply_text(f"🔑 Đang login với code: {code} ...")

    # Tạo driver
    driver = create_driver()
    driver.get("https://nullzereptool.com/")
    await asyncio.sleep(2)

    # Nhập code
    try:
        input_box = driver.find_element(By.ID, "code")
        input_box.send_keys(code)
    except:
        await update.message.reply_text("❌ Không tìm thấy ô nhập code.")
        return

    await asyncio.sleep(1)

    # Click login
    try:
        button = driver.find_element(By.XPATH, "//button[contains(text(),'Get My Dragon City Information')]")
        button.click()
    except:
        await update.message.reply_text("❌ Không thấy nút login.")
        return

    await asyncio.sleep(10)

    # Ẩn modal nếu có
    try:
        close_btn = driver.find_element(By.ID, "newsModalClose")
        close_btn.click()
    except:
        pass

    # Mở tab Resources
    try:
        res_btn = driver.find_element(By.CSS_SELECTOR, "button[data-tab='resources']")
        res_btn.click()
    except:
        pass

    await update.message.reply_text("✅ Login xong. Dùng /stats để tự động claim.")

# ==========================
# Auto claim loop
# ==========================
async def auto_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, driver

    while not stop_flag:
        try:
            button = driver.find_element(By.ID, "claim-gold-xp")
            button.click()

            # Gửi tin nhắn qua context.bot (không dùng update.message)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="💰 Claim thành công!"
            )

        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠️ Lỗi claim: {e}"
            )

        await asyncio.sleep(5)

# ==========================
# /stats → bắt đầu auto claim
# ==========================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global task, stop_flag

    if driver is None:
        await update.message.reply_text("❌ Chưa login. Dùng /login CODE trước.")
        return

    if task is not None and not task.done():
        await update.message.reply_text("⚠️ Auto claim đang chạy.")
        return

    await update.message.reply_text("▶️ Bắt đầu auto claim ...")
    stop_flag = False

    # Tạo task chạy nền đúng cách
    task = asyncio.create_task(auto_claim(update, context))

# ==========================
# /stop → dừng claim
# ==========================
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_flag, task

    if task is None or task.done():
        await update.message.reply_text("❗ Auto claim chưa chạy.")
        return

    stop_flag = True
    task = None

    await update.message.reply_text("🛑 Đã dừng auto claim.")

# ==========================
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /check. Refresh trang và lấy thông tin user mới nhất."""
    global driver

    if driver is None:
        await update.message.reply_text("❌ Chưa login. Dùng /login CODE trước.")
        return

    await update.message.reply_text("🔄 Đang làm mới trang và lấy thông tin user...")
    
    try:
        # 1. Refresh the page
        driver.refresh()
        
        # 2. Wait for a key element to be present after refresh
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "claim-gold-xp"))
        )
        
        # 3. Re-click the Resources tab to ensure stat elements are visible
        try:
            res_btn = driver.find_element(By.CSS_SELECTOR, "button[data-tab='resources']")
            res_btn.click()
            await asyncio.sleep(1) 
        except:
            # Bỏ qua nếu không click được, có thể tab đã được mở
            pass 
        
        # Helper function để lấy text/value từ ID một cách an toàn
        def get_stat(id_name):
            try:
                element = driver.find_element(By.ID, id_name)
                # Lấy giá trị từ input/textarea
                if element.tag_name in ['input', 'textarea']:
                    return element.get_attribute('value') or "0"
                # Lấy text
                text_content = element.text.strip()
                if not text_content and element.get_attribute('innerText'):
                    return element.get_attribute('innerText').strip() or "0"
                return text_content or "0"
            except:
                return "0"
                
        # Lấy thông tin
        # user_id_input là ID phổ biến cho trường chứa ID người dùng sau khi login
        user_id = get_stat("user_id_input") 
        if user_id == "0":
             user_id = "N/A (Chưa lấy được)"

        gold = get_stat("gold")
        food = get_stat("food")
        gems = get_stat("gems")
        level = get_stat("level")
        exp = get_stat("exp")
        
        # 4. Format và gửi thông tin
        
        message = (
            "📊 *THÔNG TIN TÀI KHOẢN* 📊\n\n"
            f"👤 *User ID:* `{user_id}`\n"
            f"🌟 *Level:* {level}\n"
            f"✨ *EXP:* {exp}\n\n"
            f"💰 *Tài Nguyên:*\n"
            f"  - Vàng (Gold): {gold}\n"
            f"  - Thức ăn (Food): {food}\n"
            f"  - Đá quý (Gems): {gems}\n\n"
            "✅ Dữ liệu đã được làm mới thành công."
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi làm mới/lấy dữ liệu: {e.__class__.__name__}. Vui lòng thử lại.")
        print(f"Check error: {e}")
# /out → đóng Selenium
# ==========================
async def out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global driver, stop_flag, task

    stop_flag = True
    task = None

    if driver:
        driver.quit()
        driver = None

    await update.message.reply_text("🚪 Đã đóng trình duyệt.")

# ==========================
# Run bot
# ==========================
TOKEN = "8029102657:AAF536W2Fh0ihZdCIC92dDAAWHqpwqPrVXo"
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("login", login))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("out", out))
app.add_handler(CommandHandler("check", check))
app.run_polling()
