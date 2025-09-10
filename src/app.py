from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import logging
import uuid
import threading
import gc
import re
from datetime import datetime, timedelta
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import PyPDF2
import torch

# Flask uygulaması
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global değişkenler
embedder = None
text_generator = None
faiss_index = None
document_chunks = []
document_store = {}
upload_progress = {}

class TurkishRAGSystem:
    def __init__(self):
        self.embedder = None
        self.generator = None
        self.faiss_index = None
        self.chunks = []
        
    def initialize_models(self):
        """Modelleri yükle"""
        if self.embedder is None:
            logger.info("🇹🇷 Türkçe embedding modeli yükleniyor...")
            self.embedder = SentenceTransformer('dbmdz/bert-base-turkish-128k-uncased')
            logger.info("✅ Türkçe BERT embedding modeli yüklendi")
            
        if self.generator is None:
            try:
                logger.info("📥 Türkçe generation modeli yükleniyor...")
                tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-small')
                model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
                
                self.generator = {
                    'tokenizer': tokenizer,
                    'gen_model': model
                }
                logger.info("✅ Generation modeli yüklendi")
            except Exception as e:
                logger.warning(f"⚠️ Generation modeli yüklenemedi: {e}")
                self.generator = None
    
    def normalize_turkish_text(self, text):
        """Türkçe karakterleri normalize et"""
        if not text:
            return text
        
        replacements = {
            'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 
            'ü': 'u', 'Ü': 'U', 'ş': 's', 'Ş': 'S',
            'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
        }
        
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        
        return text
    
    def extract_keywords(self, query):
        """Soruden anahtar kelimeleri çıkar"""
        stop_words = {
            'bir', 'bu', 'su', 've', 'veya', 'ile', 'icin', 'de', 'da', 'den', 'dan', 
            'te', 'ta', 'nedir', 'ne', 'nasil', 'neden', 'kim', 'hakkinda', 'olan',
            'gibi', 'kadar', 'daha', 'en', 'cok', 'az', 'var', 'yok', 'mi', 'mu'
        }
        
        normalized_query = self.normalize_turkish_text(query.lower())
        words = [word.strip('.,!?()[]') for word in normalized_query.split()]
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def extract_text_from_pdf(self, pdf_file):
        """PDF'den metin çıkar"""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF okuma hatası: {e}")
            return None
    
    def create_chunks(self, text, chunk_size=400, overlap=50):
        """Metni parçalara böl"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) > 50:  # Çok kısa parçaları atla
                chunks.append(chunk_text.strip())
        
        return chunks
    
    def create_faiss_index(self, chunks):
        """FAISS indexi oluştur"""
        if not chunks:
            return None
        
        # Embedding'leri oluştur
        embeddings = self.embedder.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
        
        # FAISS index oluştur
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        index.add(embeddings.astype('float32'))
        
        logger.info(f"FAISS index oluşturuldu: {len(chunks)} chunk, {dimension} boyut")
        return index
    
    def search_chunks(self, query, top_k=5):
        """Hibrit arama: Embedding + Kelime eşleşmesi"""
        if not query or not self.faiss_index or not self.chunks:
            return []
        
        # Anahtar kelimeleri çıkar
        keywords = self.extract_keywords(query)
        
        # Query embedding
        query_vec = self.embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        
        # FAISS arama
        scores, indices = self.faiss_index.search(query_vec.astype('float32'), len(self.chunks))
        
        results = []
        
        for i in range(len(scores[0])):
            if indices[0][i] < len(self.chunks):
                chunk_text = self.chunks[indices[0][i]]
                normalized_chunk = self.normalize_turkish_text(chunk_text.lower())
                
                # Embedding skoru
                embedding_score = float(scores[0][i])
                
                # Kelime eşleşmesi skoru
                keyword_matches = 0
                for keyword in keywords:
                    if keyword in normalized_chunk:
                        keyword_matches += 1
                
                # Hibrit skor
                if keyword_matches > 0:
                    hybrid_score = (keyword_matches / len(keywords)) * 0.8 + embedding_score * 0.2
                else:
                    hybrid_score = embedding_score * 0.1  # Kelime eşleşmesi yoksa düşük skor
                
                results.append({
                    'text': chunk_text,
                    'score': hybrid_score,
                    'keyword_matches': keyword_matches,
                    'embedding_score': embedding_score
                })
        
        # Skorlara göre sırala ve en iyi sonuçları döndür
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, query, search_results):
        """Cevap üret"""
        if not search_results:
            return "Bu konuda bilgi bulunamadı."
        
        # En iyi sonucu al
        best_result = search_results[0]
        
        # Eğer kelime eşleşmesi varsa direkt chunk'tan cevap ver
        if best_result['keyword_matches'] > 0:
            chunk_text = best_result['text']
            
            # Ana kelimeyi içeren en iyi cümleyi bul
            sentences = [s.strip() for s in chunk_text.split('.') if s.strip()]
            
            keywords = self.extract_keywords(query)
            normalized_query = self.normalize_turkish_text(query.lower())
            
            best_sentence = None
            best_match_count = 0
            
            for sentence in sentences:
                if len(sentence.split()) < 3:  # Çok kısa cümleler
                    continue
                    
                normalized_sentence = self.normalize_turkish_text(sentence.lower())
                match_count = sum(1 for kw in keywords if kw in normalized_sentence)
                
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_sentence = sentence
            
            if best_sentence and best_match_count > 0:
                return best_sentence.strip() + ('.' if not best_sentence.endswith('.') else '')
        
        # Fallback: İlk chunk'ın başından cevap ver
        chunk_text = best_result['text']
        sentences = [s.strip() for s in chunk_text.split('.') if s.strip() and len(s.split()) >= 4]
        
        if sentences:
            return sentences[0] + ('.' if not sentences[0].endswith('.') else '')
        
        return "Bu konuda yeterli bilgi bulunamadı."

# Global RAG sistemi
rag_system = TurkishRAGSystem()

def initialize_models():
    """Modelleri yükle"""
    global embedder, text_generator
    rag_system.initialize_models()
    embedder = rag_system.embedder
    text_generator = rag_system.generator

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'PDF dosyası bulunamadı'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Sadece PDF dosyaları desteklenir'}), 400
        
        # Modelleri yükle
        initialize_models()
        
        # PDF'i işle
        logger.info(f"PDF işleniyor: {file.filename}")
        
        text = rag_system.extract_text_from_pdf(file)
        if not text:
            return jsonify({'error': 'PDF metni çıkarılamadı'}), 400
        
        logger.info(f"Çıkarılan metin uzunluğu: {len(text)} karakter")
        
        # Chunk'lara böl
        chunks = rag_system.create_chunks(text)
        logger.info(f"Metin {len(chunks)} parçaya bölündü")
        
        if not chunks:
            return jsonify({'error': 'Metin parçalara bölünemedi'}), 400
        
        # FAISS index oluştur
        faiss_index = rag_system.create_faiss_index(chunks)
        if faiss_index is None:
            return jsonify({'error': 'Arama indexi oluşturulamadı'}), 400
        
        # Global değişkenleri güncelle
        global document_chunks
        rag_system.chunks = chunks
        rag_system.faiss_index = faiss_index
        document_chunks = chunks
        
        document_store[file.filename] = {
            'upload_time': datetime.now().isoformat(),
            'chunks': len(chunks),
            'text_length': len(text)
        }
        
        logger.info(f"Doküman başarıyla yüklendi: {file.filename} - {len(chunks)} chunk")
        
        return jsonify({
            'success': True,
            'message': f'PDF başarıyla yüklendi ve işlendi',
            'filename': file.filename,
            'chunks': len(chunks),
            'text_length': len(text)
        })
        
    except Exception as e:
        logger.error(f"Upload hatası: {e}")
        return jsonify({'error': f'Dosya yüklenirken hata: {str(e)}'}), 500

@app.route('/query', methods=['POST'])
def process_query():
    try:
        data = request.get_json()
        if not data or not data.get('query'):
            return jsonify({'error': 'Soru boş olamaz'}), 400
        
        query = data['query'].strip()
        if len(query) < 3:
            return jsonify({'error': 'Soru çok kısa'}), 400
        
        if not rag_system.chunks or not rag_system.faiss_index:
            return jsonify({'error': 'Önce bir PDF yükleyin'}), 400
        
        logger.info(f"Soru işleniyor: {query}")
        
        # Arama yap
        search_results = rag_system.search_chunks(query, top_k=5)
        
        if not search_results:
            return jsonify({
                'answer': 'Bu soru ile ilgili bilgi bulunamadı.',
                'confidence': 0
            })
        
        # En yüksek skoru kontrol et
        max_score = search_results[0]['score']
        
        if max_score < 0.1:
            return jsonify({
                'answer': 'Bu soru için yeterli benzerlik bulunamadı. Lütfen dokümandaki konular hakkında soru sorun.',
                'confidence': max_score
            })
        
        # Cevap üret
        answer = rag_system.generate_answer(query, search_results)
        
        logger.info(f"Cevap üretildi: {answer[:100]}...")
        
        return jsonify({
            'answer': answer,
            'confidence': max_score,
            'keyword_matches': search_results[0]['keyword_matches']
        })
        
    except Exception as e:
        logger.error(f"Query işleme hatası: {e}")
        return jsonify({'error': f'Soru işlenirken hata: {str(e)}'}), 500

@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify({
        'documents': document_store,
        'total_chunks': len(rag_system.chunks)
    })

@app.route('/clear', methods=['POST'])
def clear_documents():
    try:
        global document_store
        rag_system.chunks = []
        rag_system.faiss_index = None
        document_store = {}
        gc.collect()
        
        logger.info("Tüm dokümanlar temizlendi")
        return jsonify({'success': True, 'message': 'Tüm dokümanlar temizlendi'})
        
    except Exception as e:
        logger.error(f"Temizleme hatası: {e}")
        return jsonify({'error': 'Temizleme sırasında hata oluştu'}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Dosya çok büyük (max 50MB)'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Sunucu hatası oluştu'}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint bulunamadı'}), 404

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Temiz RAG sistemi başlatılıyor - Port: {port}")
    
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port,
        threaded=True
    )
