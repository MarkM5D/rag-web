# RAG Web Uygulaması

# 🤖 Türkçe RAG Web Uygulaması

Modern ve kullanıcı dostu **Retrieval-Augmented Generation (RAG)** sistemi. PDF belgelerinden bilgi çıkarıp, Türkçe sorulara akıllı cevaplar verir.

## ✨ Özellikler

- 🇹🇷 **Türkçe Desteği**: Türkçe karakterleri normalize eder
- 🔍 **Hibrit Arama**: Embedding + Kelime eşleşmesi kombinasyonu
- 📱 **Responsive Design**: Mobil ve masaüstü uyumlu
- 🚀 **Hızlı Yanıt**: Optimized chunk processing
- 🎯 **Doğru Cevaplar**: Her soruya PDF içeriğinden özel cevap
- 🧹 **Temiz Kod**: SOLID prensiplere uygun mimari

## 🛠 Teknolojiler

- **Backend**: Flask 3.1.0, Python 3.11+
- **AI/ML**: 
  - SentenceTransformers (Türkçe BERT)
  - FAISS (Vector Search)
  - Transformers (T5 Generation)
- **Frontend**: Vanilla JavaScript, Modern CSS
- **PDF Processing**: PyPDF2

## 📦 Kurulum

### 1. Repository'yi klonlayın
```bash
git clone https://github.com/MarkM5D/rag-web.git
cd rag-web
```

### 2. Virtual Environment oluşturun
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac  
source .venv/bin/activate
```

### 3. Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### 4. Uygulamayı başlatın
```bash
python app.py
```

Tarayıcıdan `http://127.0.0.1:5000` adresini ziyaret edin.

## 🚀 Kullanım

1. **PDF Yükle**: Sol panelden PDF dosyanızı sürükleyin veya seçin
2. **Analiz**: Sistem PDF'i otomatik analiz eder ve parçalar
3. **Soru Sor**: Sağ panelden PDF içeriği hakkında sorular sorun
4. **Cevap Al**: AI destekli akıllı cevapları alın

### Örnek Sorular
```
- "Mouse nedir?"
- "USB bellek özellikleri nelerdir?"  
- "Kulaklık türleri hakkında bilgi ver"
- "Sistem gereksinimleri neler?"
```

## 📋 Sistem Gereksinimleri

- **Python**: 3.11 veya üstü
- **RAM**: 4GB+ (model yükleme için)
- **Disk**: 2GB+ boş alan
- **İnternet**: İlk çalıştırmada model indirme için

## 🏗 Mimari

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Upload    │───▶│  Text Extraction │───▶│   Chunking      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Hybrid Search   │◀───│ FAISS Indexing │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                      │
         │              ┌──────────────────┐
         └─────────────▶│ Answer Generation│
                        └──────────────────┘
```

### Hibrit Arama Algoritması
- **%80 Kelime Eşleşmesi**: Doğrudan keyword matching
- **%20 Embedding Similarity**: Semantic similarity
- **Türkçe Normalizasyon**: ı→i, ğ→g, ü→u, ş→s, ö→o, ç→c

## 🔧 Konfigürasyon

### Environment Variables
```env
FLASK_ENV=development
PORT=5000
MAX_CONTENT_LENGTH=50MB
```

### Model Settings
```python
# Turkish BERT Embeddings
EMBEDDER_MODEL = 'dbmdz/bert-base-turkish-128k-uncased'

# Text Generation
GENERATOR_MODEL = 'google/flan-t5-small'

# Chunking
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
```

## 📊 Performans

- **PDF İşleme**: ~2-5 saniye (sayfa sayısına göre)
- **İlk Model Yükleme**: ~30-60 saniye
- **Soru-Cevap**: ~1-3 saniye
- **Memory Usage**: ~2-4GB (model bağımlı)

## 🐛 Troubleshooting

### Yaygın Sorunlar

**1. Model İndirme Hatası**
```bash
# İnternet bağlantısını kontrol edin
# Firewall/antivirus ayarlarını kontrol edin
```

**2. Memory Error**
```bash
# System RAM'i artırın (min 4GB)
# Diğer uygulamaları kapatın
```

**3. PDF Okuma Hatası**
```bash
# PDF'in bozuk olmadığından emin olun
# Şifreli PDF'leri desteklemez
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Branch'e push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasını inceleyin.

## 👨‍💻 Geliştirici

**Mehmet Salih Durdu**
- GitHub: [@MarkM5D](https://github.com/MarkM5D)

## 🙏 Teşekkürler

- HuggingFace Transformers
- FAISS Team
- Turkish NLP Community
- Flask Framework

---

⭐ Bu projeyi beğendiyseniz star vermeyi unutmayın!

## Özellikler

- 🔍 **PDF Analizi**: PDF dosyalarını yükleyip içeriğini otomatik analiz etme
- 💬 **Akıllı Soru-Cevap**: Doküman içeriğine dayalı doğal dil işleme
- 🔍 **Semantik Arama**: FAISS ile hızlı ve etkili benzerlik araması
- 🎨 **Modern Arayüz**: Responsive ve kullanıcı dostu tasarım
- 📊 **Kaynak Gösterimi**: Cevapların hangi doküman parçalarından geldiğini gösterme

## Teknolojiler

- **Backend**: Python Flask
- **AI/ML**: 
  - Sentence Transformers (çok dilli gömme)
  - Hugging Face Transformers (soru-cevap)
  - FAISS (vektör arama)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF İşleme**: PyPDF2

## Kurulum

1. **Sanal ortam oluşturun:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# veya
source .venv/bin/activate  # Linux/Mac
```

2. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Uygulamayı başlatın:**
```bash
python app.py
```

4. **Tarayıcıda açın:**
http://localhost:5000

## Kullanım

1. **PDF Yükleme**: Sol panelden bir PDF dosyası seçin ve "Yükle" butonuna tıklayın
2. **Soru Sorma**: Sağ paneldeki metin kutusuna sorunuzu yazın
3. **Cevap Alma**: Sistem doküman içeriğini analiz ederek size cevap verecek

## Proje Yapısı

```
rag-web/
├── app.py              # Ana Flask uygulaması
├── templates/
│   └── index.html      # Ana HTML template
├── static/             # CSS/JS dosyaları (gerekirse)
├── uploads/            # Geçici PDF dosyaları
├── requirements.txt    # Python bağımlılıkları
└── README.md          # Bu dosya
```

## API Endpoints

- `GET /` - Ana sayfa
- `POST /upload` - PDF dosyası yükleme
- `POST /query` - Soru sorma
- `GET /documents` - Yüklenmiş dokümanları listeleme
- `POST /clear` - Tüm dokümanları temizleme

## Özelleştirme

### AI Modellerini Değiştirme

`app.py` dosyasındaki `initialize_models()` fonksiyonunda farklı modeller kullanabilirsiniz:

```python
# Farklı bir embedding modeli
embedder = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

# Farklı bir QA modeli  
qa_pipeline = pipeline("question-answering", model="dbmdz/bert-large-cased-finetuned-conll03-english")
```

### Chunk Boyutunu Ayarlama

Doküman parçalama boyutunu `chunk_text()` fonksiyonunda değiştirebilirsiniz:

```python
def chunk_text(text, chunk_size=1000, overlap=100):  # Daha büyük parçalar
```

## Geliştirici Notları

- İlk çalıştırmada AI modelleri indirilecektir (yaklaşık 1-2 GB)
- Büyük PDF dosyaları için işleme süresi artabilir
- FAISS index'i RAM'de saklanır, sunucu yeniden başlatıldığında silinir

## Lisans

MIT License

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Destek

Sorunlar için GitHub Issues kullanın.
