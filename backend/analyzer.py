import boto3
import base64

REGION = 'us-east-1'

try:
    # Kita tetap pertahankan KMS client karena LabRole biasanya mengizinkan KMS
    kms_client = boto3.client('kms', region_name=REGION)
except Exception as e:
    print(f"[ERROR] Gagal menginisialisasi KMS client: {e}")

def analyze_sentiment(text):
    """
    Pivot Solusi: Analisis Sentimen Berbasis Kamus Bahasa Inggris (Lokal).
    Bebas dari hambatan AccessDenied AWS Academy.
    """
    # Kamus kata sederhana untuk mengecek teks berita bahasa Inggris
    positive_words = ['growth', 'up', 'rise', 'gain', 'success', 'higher', 'positive', 'boost', 'profit', 'surge']
    negative_words = ['drop', 'crash', 'down', 'fall', 'panic', 'loss', 'negative', 'crisis', 'slump', 'weakens']
    
    # Ubah teks ke huruf kecil dan pecah menjadi kata-kata
    words = text.lower().split()
    
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    
    # Tentukan hasil sentimen berdasarkan jumlah kata yang dominan
    if pos_count > neg_count:
        sentiment = "POSITIVE"
        score = (pos_count / (pos_count + neg_count)) * 100
    elif neg_count > pos_count:
        sentiment = "NEGATIVE"
        score = (neg_count / (pos_count + neg_count)) * 100
    else:
        sentiment = "NEUTRAL"
        score = 100.0
        
    return {
        'sentiment': sentiment,
        'confidence_score': round(score, 2)
    }

def encrypt_data(text, kms_key_id):
    """Fungsi enkripsi tetap dipertahankan"""
    try:
        response = kms_client.encrypt(
            KeyId=kms_key_id,
            Plaintext=text.encode('utf-8')
        )
        ciphertext_blob = response['CiphertextBlob']
        return base64.b64encode(ciphertext_blob).decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Gagal mengenkripsi data dengan KMS: {e}")
        return None