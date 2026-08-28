# شاپیار | فروشگاه آنلاین مدرن

فروشگاه کامل و مقیاس‌پذیر با Django، ورود با گوگل، پنل ادمین حرفه‌ای و UI شیک فارسی.

## ویژگی‌ها

- ✨ طراحی مدرن، RTL و کاربرپسند با Tailwind CSS
- 🔐 ورود با گوگل (اولین بار انتخاب اکانت، سپس حفظ session)
- 👤 پنل مدیریت کامل برای افزودن محصول با عکس
- 🛒 سبد خرید (مهمان + کاربر لاگین‌شده)
- 📦 سیستم سفارش
- ☁️ آماده Cloudinary برای عکس‌ها (مقیاس‌پذیر روی Render)
- 🚀 آماده دیپلوی روی Render

**اکانت ادمین:** `shapyaar@gmail.com` (با ورود گوگل به صورت خودکار staff/superuser می‌شود)

---

## نصب لوکال

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# مقادیر GOOGLE_CLIENT_ID و GOOGLE_CLIENT_SECRET را پر کنید
python manage.py migrate
python manage.py createsuperuser   # اختیاری
python manage.py runserver
```

سایت روی http://127.0.0.1:8000 باز می‌شود.

### تنظیم Google OAuth

1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. پروژه جدید بسازید
3. APIs & Services → Credentials → Create OAuth client ID (Web application)
4. Authorized redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `https://YOUR-APP.onrender.com/accounts/google/login/callback/`
5. Client ID و Secret را در `.env` بگذارید

در پنل ادمین Django هم می‌توانید Social Application برای Google اضافه کنید (Site = example.com یا دامنه شما).

---

## دیپلوی روی Render

1. این ریپو را به GitHub پوش کنید
2. در Render → New → Web Service
3. ریپو را وصل کنید
4. تنظیمات:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn shopyaar.wsgi:application`
   - **Environment:** Python 3
5. Environment Variables اضافه کنید:
   - `SECRET_KEY` (یک رشته تصادفی قوی)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=.onrender.com`
   - `DATABASE_URL` (از Render PostgreSQL)
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - (اختیاری) `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`

6. یک PostgreSQL database در Render بسازید و به سرویس وصل کنید.

### Cloudinary (توصیه قوی برای عکس‌ها)

چون فایل‌سیستم Render موقتی است، برای ذخیره دائمی عکس محصولات:

1. حساب رایگان در [Cloudinary](https://cloudinary.com) بسازید
2. Cloud name, API Key, API Secret را در Environment Variables بگذارید

---

## ساختار پروژه

```
shopyaar/          # تنظیمات پروژه
store/             # مدل‌ها، ویوها، ادمین فروشگاه
accounts/          # سیگنال‌های ادمین گوگل
templates/         # قالب‌های فارسی شیک
static/            # فایل‌های استاتیک
```

## پنل ادمین

بعد از ورود با `shapyaar@gmail.com` به `/admin/` بروید و دسته‌بندی + محصول با عکس اضافه کنید.

موفق باشید! 🛍️
