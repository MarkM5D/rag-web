# RAG Web Projesi Başlatma Script'i
Write-Host "RAG Web Projesi başlatılıyor..." -ForegroundColor Green

# Sanal ortamı etkinleştir
Write-Host "Sanal ortam etkinleştiriliyor..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Gerekli paketlerin yüklü olup olmadığını kontrol et ve eksikleri yükle
Write-Host "Gerekli paketler kontrol ediliyor..." -ForegroundColor Yellow
$packages = @("flask", "flask-cors", "sentence-transformers", "faiss-cpu", "PyPDF2", "transformers", "torch", "numpy", "werkzeug")

foreach ($package in $packages) {
    $installed = pip show $package 2>$null
    if (-not $installed) {
        Write-Host "$package paketi bulunamadı, yükleniyor..." -ForegroundColor Red
        pip install $package
    } else {
        Write-Host "$package paketi zaten yüklü ✓" -ForegroundColor Green
    }
}

# Tüm paketleri requirements.txt'den yükle (güvenlik için)
Write-Host "Requirements.txt'den paketler yükleniyor..." -ForegroundColor Yellow
pip install -r requirements.txt

# uploads klasörünü oluştur (yoksa)
if (-not (Test-Path "uploads")) {
    New-Item -ItemType Directory -Name "uploads"
    Write-Host "uploads klasörü oluşturuldu." -ForegroundColor Green
}

# Flask uygulamasını başlat
Write-Host "Flask uygulaması başlatılıyor..." -ForegroundColor Green
Write-Host "Uygulama http://localhost:5000 adresinde çalışacak" -ForegroundColor Cyan
Write-Host "Uygulamayı durdurmak için Ctrl+C tuşlarına basın" -ForegroundColor Cyan

python app.py
