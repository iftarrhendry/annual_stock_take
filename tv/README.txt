AST TV DASHBOARD - STATIC VERSION
=================================

Tujuan
------
Versi ini dibuat khusus untuk browser Smart TV / meeting display.
Tidak memakai frontend Streamlit, sehingga lebih ringan dan lebih kompatibel
dengan browser TV yang lama.

Struktur folder yang disarankan di repo annual_stock_take:

annual_stock_take/
│
├── app.py
├── data/
│   └── DATA_AST_LSI.xlsx
│
└── tv/
    ├── index.html
    ├── data.json
    ├── build_tv_data.py
    └── assets/
        ├── logo.png
        └── ast_warehouse.jpg


LANGKAH 1 - COPY ASSET
----------------------
Copy dari project utama:

assets/logo.png
-> tv/assets/logo.png

assets/ast_warehouse.jpg
-> tv/assets/ast_warehouse.jpg


LANGKAH 2 - BUAT DATA JSON AKTUAL
---------------------------------
Pastikan folder tv berada di dalam project annual_stock_take.

Jalankan dari terminal project:

python tv/build_tv_data.py

Script membaca:
data/DATA_AST_LSI.xlsx

dan membuat:
tv/data.json


LANGKAH 3 - TEST LOKAL
----------------------
JANGAN membuka index.html dengan double-click / file:// karena browser dapat
memblokir pembacaan data.json.

Dari folder project jalankan:

python -m http.server 8000

Lalu buka:

http://localhost:8000/tv/


Untuk testing dari HP / TV pada jaringan yang sama:

python -m http.server 8000 --bind 0.0.0.0

Cek IP laptop dengan:

ipconfig

Lalu buka di TV/HP:

http://IP-LAPTOP:8000/tv/


FITUR
-----
- Filter Batch
- Filter Store
- KPI Total / Upcoming / Today / Completed
- Progress AST
- Batch View
- Tombol LIHAT AST
- Store Countdown realtime WIB
- WH LSI (H-14)
- Coordinator
- Team AST
- Fullscreen countdown
- Fullscreen seluruh dashboard
- Jadwal AST table
- JavaScript dibuat tanpa framework / dependency eksternal


DEPLOY
------
Untuk link permanen Smart TV, versi ini cocok di-host sebagai static site.
Opsi paling sederhana: GitHub Pages.

Kita bisa atur GitHub Pages setelah versi lokal ini lolos tes pada browser TV.


UPDATE DATA
-----------
Setiap DATA_AST_LSI.xlsx berubah:

1. Save Excel
2. Jalankan:
   python tv/build_tv_data.py
3. Commit tv/data.json bersama update Excel
4. Push

Dengan begitu Streamlit dan TV tetap memakai sumber data Excel yang sama.


CATATAN
-------
data.json bawaan paket ini adalah DEMO DATA agar index.html langsung bisa
dites. Setelah menjalankan build_tv_data.py, demo data akan otomatis
diganti data aktual.
