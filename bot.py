from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler
import requests
from bs4 import BeautifulSoup
import config
async def gettt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tt = update.message.text.replace('/', '')
    cookies = {}
    wp_login = 'https://zarfilm.com/wp-login.php'
    wp_admin = 'https://zarfilm.com'
    username = config.USER_NAME
    password = config.PASS
    headers1 = { 'Cookie':'wordpress_test_cookie=WP Cookie check' }
    datas={ 
            'log':username, 'pwd':password, 'wp-submit':'Log In', 
            'redirect_to':wp_admin, 'testcookie':'1'  
        }
    #to get redirect url
    r = requests.head(wp_login, allow_redirects=True)
    wp_login = r.url
    #login
    y = requests.post(wp_login,data=datas)
    for key, value in y.cookies.get_dict().items():   # iter on both keys and values
        if key.startswith('wordpress_logged_in'):
            cookies = {key : value}
    print(cookies)
    x = requests.get("https://zarfilm.com/"+tt, cookies=cookies)
    soup = BeautifulSoup(x.text, 'html.parser')
    message = ''
    if "item_season" in x.text:
        for season in soup.find_all('div','item_season'):
            season_name = season.find('span','label_text_row').text
            #print(season_name)
            qualities = season.find_all('div','item_quality_season')
            message = message+season_name+'\n'
            for quality in qualities:
                quality_name = quality.find('div','value_text_head_right_qulity').text
                episodes = quality.find_all('a','dllinkhref')
                message = message +'\n'+ quality_name + '\n'+ str(episodes)
            try:
                #print(len(message))
                await update.message.reply_text(message, parse_mode="HTML")
            except:
                #print(len(message))
                message = message.split('\n')
                print(message)
                t = ''
                for m in message[:len(message) // 2]:
                    t=t+m+'\n'
                await update.message.reply_text(t, parse_mode="HTML")
                t=''
                for m in message[len(message) // 2:]:
                    t=t+m+'\n'
                await update.message.reply_text(t, parse_mode="HTML")
            message = ''
    else:
        for dllink_box in soup.find_all('div','dllink_box'):
            title = dllink_box.find('span','title_text_dllink').text
            message = message+title+'\n'
            items = dllink_box.find_all('div','item_dllink_box')
            for item in items:
                url = item.find('a','btndllinks').get('href')
                quality = item.find('div','quality_text').text
                message = message +'<a href="'+url+'">'+quality+'</a>\n'
        await update.message.reply_text(message, parse_mode="HTML")
    await update.message.reply_text('برای استفاده از لینک های بالا حتما فیلترشکن خود را خاموش کنید!', parse_mode="HTML")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.message.text
    x = requests.get('https://zarfilm.com/?s='+query)
    soup = BeautifulSoup(x.text, 'html.parser')
    titles = soup.find_all('div','title_item_holder')
    message = ''
    for title in titles:
        message = message+title.a.text+' /'+title.a.get('href').split('/')[-2]+'\n'
    await update.message.reply_text(message, parse_mode="HTML")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.message.reply_text('سلام، به ربات فیلم و سریال دوغ خوش‌آمدید.\nاسم هر فیلمی رو که می‌خوای برای من به صورت انگلیسی یا فارسی بفرست تا برات جستجو کنم:', parse_mode="HTML")

app = ApplicationBuilder().token(config.TOKEN).build()

app.add_handler(CommandHandler('start',start))
app.add_handler(MessageHandler(filters.Regex("^/tt"), gettt))
app.add_handler(MessageHandler(filters.Regex(""),search))
app.run_polling()