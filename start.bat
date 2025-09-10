@echo off
echo RAG Web Projesi baslatiliyor...
echo.

echo Sanal ortam etkinlestiriliyor...
call .venv\Scripts\activate.bat

echo.
echo Gerekli paketler yukleniyor...
pip install -r requirements.txt

echo.
echo uploads klasoru kontrol ediliyor...
if not exist "uploads" mkdir uploads

echo.
echo Flask uygulamasi baslatiliyor...
echo Uygulama http://localhost:5000 adresinde calisacak
echo Uygulamayi durdurmak icin Ctrl+C tushlarina basin
echo.
echo AI modelleri ilk calistirmada otomatik yuklenecek...
echo Lutfen sabir gosterin...
echo.

set FLASK_ENV=development
python app.py

pause
