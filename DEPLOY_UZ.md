# Memory Vault — ishga tushirish

1. `pip install -r requirements.txt`
2. `.env.example` nusxasini `.env` deb nomlang va sozlang.
3. Telegram botni yopiq kanalga **administrator** qilib qo‘shing. Kanalning raqamli `-100...` ID raqamini `DB_CHANNEL_ID` ga kiriting. Taklif havolasi ID o‘rnini bosa olmaydi.
4. Supabase PostgreSQL bazasini yarating, **connection string** ni `DATABASE_URL` ga yozing. Supabase pooler connection string ishlatish mumkin (IPv4 hostinglar uchun). Maxfiy kalitlarni GitHub'ga joylamang.
5. `ADMIN_ID` ga @Yusu1F_m1 ning raqamli Telegram ID sini kiriting. Username tekshiruvi ham mavjud, lekin ID xavfsizroq.
6. `python main.py` ni ishga tushiring.
7. Hosting almashganda **bir xil BOT_TOKEN, DATABASE_URL va DB_CHANNEL_ID** dan foydalaning. Eski hostingdagi bot jarayonini to‘xtating.

## Eski ma'lumotlar
`memory_vault_data.json` fayli bo‘lsa, dastur ishga tushganda mavjud yozuvlarni bazaga bir marta import qiladi (mavjud yozuvlarni ustidan yozmaydi). Avval eski serverdagi eng so‘nggi JSON faylning zaxira nusxasini oling.

## Eslatmalar
Eslatmalar bot orqali shaxsiy Telegram xabari sifatida yuboriladi, telefon SMS emas. `TIMEZONE` standart `Asia/Tashkent`. Bot ishlayotgan bo‘lishi kerak. Rejalashtiruvchi har 60 soniyada tekshiradi.

## Cheklovlar
Bu versiya mavjud fayl va menyularni saqlaydi. Eski handlerlar `load_data/save_data` usulida barcha foydalanuvchilarni birdan o‘qib-yozadi: bir nechta bot nusxasini parallel ishlatmang, aks holda yozuvlar bir-birini bosib ketishi mumkin. Telegram kanalidan faylni tiklash uchun botning kanaldagi admin huquqi va xabar mavjudligi zarur. Botni kanaldan chiqarmang. Kanalga oldin yuborilmagan eski fayllarni avtomatik tiklab bo‘lmaydi.
