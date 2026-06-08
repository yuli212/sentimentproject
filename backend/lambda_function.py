import json
import boto3
import uuid
from datetime import datetime

# Mengimpor modul buatan kita sebelumnya
import scraper
import analyzer

# Inisialisasi koneksi ke Amazon DynamoDB
# Pastikan nama tabel sesuai dengan yang akan dibuat di AWS Console nanti
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SentimentHistory')

# KMS Key ID (Nanti diganti dengan ARN asli dari AWS Console)
KMS_KEY_ID = "arn:aws:kms:us-east-1:629478360569:key/a527c2a7-f3d8-4b86-be99-adfeaebc2c84"

def lambda_handler(event, context):
    """
    Fungsi utama yang akan dipanggil oleh AWS Lambda saat dipicu oleh API Gateway.
    """
    # 1. Konfigurasi CORS (Cross-Origin Resource Sharing)
    # Sangat krusial! Tanpa ini, browser akan memblokir web S3 milikmu saat mencoba memanggil API ini.
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    try:
        # Menangkap rute path dan metode HTTP dari API Gateway
        http_method = event.get('httpMethod')
        path = event.get('path')

        # 2. Handle CORS Preflight Request
        if http_method == 'OPTIONS':
            return {"statusCode": 200, "headers": headers, "body": json.dumps("CORS OK")}

        # ========================================================
        # RUTE 1: /get-news (Fase 1 - Mengambil Daftar Berita)
        # ========================================================
        if path == '/get-news' and http_method == 'GET':
            # Mengambil parameter keyword dari URL (misal: /get-news?keyword=dollar)
            query_params = event.get('queryStringParameters') or {}
            keyword = query_params.get('keyword', 'dollar')
            
            # Memanggil modul scraper.py
            news_list = scraper.fetch_news(keyword, max_results=5)
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Berhasil mengambil berita",
                    "data": news_list
                })
            }

        # ========================================================
        # RUTE 2: /analyze (Fase 2 - Analisis AI & Simpan ke DB)
        # ========================================================
        elif path == '/analyze' and http_method == 'POST':
            # Membaca data yang dikirim oleh JavaScript dari browser
            body = json.loads(event.get('body', '{}'))
            news_title = body.get('title', '')
            news_summary = body.get('summary', '')

            # A. Proses Analisis AI (Memanggil analyzer.py)
            text_to_analyze = news_summary if news_summary else news_title
            ai_result = analyzer.analyze_sentiment(text_to_analyze)

            # B. Proses Enkripsi Keamanan (Memanggil analyzer.py)
            encrypted_text = analyzer.encrypt_data(text_to_analyze, KMS_KEY_ID)

            # C. Proses Penyimpanan Database (DynamoDB)
            # Menghasilkan ID unik untuk setiap rekaman
            record_id = str(uuid.uuid4())
            waktu_sekarang = datetime.utcnow().isoformat()

            table.put_item(
                Item={
                    'RecordID': record_id,           # Partition Key di DynamoDB
                    'Timestamp': waktu_sekarang,     # Sort Key di DynamoDB
                    'Title': news_title,
                    'Sentiment': ai_result['sentiment'],
                    'Confidence': str(ai_result['confidence_score']),
                    'Encrypted_Text': encrypted_text or "ENCRYPTION_FAILED"
                }
            )

            # Mengembalikan hasil akhir ke web browser
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Analisis selesai dan tersimpan aman di database.",
                    "sentiment": ai_result['sentiment'],
                    "confidence": ai_result['confidence_score']
                })
            }

        # Jika rute tidak ditemukan
        else:
            return {
                "statusCode": 404, 
                "headers": headers, 
                "body": json.dumps("Rute API tidak ditemukan.")
            }

    except Exception as e:
        print(f"[FATAL ERROR] {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Terjadi kesalahan internal pada server."})
        }