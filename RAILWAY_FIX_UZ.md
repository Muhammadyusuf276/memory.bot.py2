# MemoryBot — Railway sozlash

1. Railway Variables: `BOT_TOKEN`, `ADMIN_USERNAME=Yusu1F_m1`, `ADMIN_ID=0` (yoki /myid dan haqiqiy ID), `DATABASE_URL`, `DB_CHANNEL_ID`, `TIMEZONE=Asia/Tashkent`.
2. Telegram @Yusu1F_m1 akkauntidan botga `/myid` va `/admin` yuboring. Username Telegram Settings da aynan `Yusu1F_m1` bo'lishi kerak. Username o'zgaruvchan, shuning uchun /myid dagi doimiy raqamni ADMIN_ID ga kiritish tavsiya etiladi.
3. Kanalga botni admin sifatida qo'shing, Post Messages huquqini yoqing. Kanaldagi yangi postni botga forward qiling: u haqiqiy `-100...` kanal ID sini ko'rsatadi. Uni Railway Variables → `DB_CHANNEL_ID` ga kiriting. Invite link ID o'rnini bosa olmaydi.
4. Railway redeploy, `/checkchannel` bilan sinov.
5. Fayl saqlash uchun botda papka yarating → Fayl Yuklash → papka tanlash → rasm yuborish.
6. `DATABASE_URL` doimiy Postgres bo'lishi kerak. Railway ephemeral diskdagi JSON server almashtirilganda saqlanmaydi.

⚠️ Botni haqiqiy Telegram/Railway bilan tekshirish uchun token va kanal admin huquqlari talab qilinadi. Ularni chatga yubormang.
