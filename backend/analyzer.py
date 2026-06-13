import boto3
import base64
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

REGION = 'us-east-1'

try:
    # Maintain connection to AWS KMS security system
    kms_client = boto3.client('kms', region_name=REGION)
except Exception as e:
    print(f"[ERROR] Failed to initialize KMS client: {e}")

# Initialize VADER
nlp_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Sentiment analysis using VADER NLP algorithm.
    Can detect grammar, negation, and emotional intensity.
    """
    # Generate sentiment score dictionary 
    scores = nlp_analyzer.polarity_scores(text)
    
    # 'compound' score is VADER's primary metric (ranges from -1 to 1)
    compound = scores['compound']
    
    #  Classification logic for VADER 
    if compound >= 0.05:
        sentiment = "POSITIVE"
        # Convert compound score to confidence percentage (0-100%)
        confidence = compound * 100
    elif compound <= -0.05:
        sentiment = "NEGATIVE"
        # Use absolute value to keep confidence positive
        confidence = abs(compound) * 100
    else:
        sentiment = "NEUTRAL"
        # If neutral, use VADER's 'neu' score as percentage
        confidence = scores['neu'] * 100
        
    return {
        'sentiment': sentiment,
        'confidence_score': round(confidence, 2)
    }

def encrypt_data(text, kms_key_id):
    """KMS encryption function remains unchanged, secures text to binary"""
    try:
        response = kms_client.encrypt(
            KeyId=kms_key_id,
            Plaintext=text.encode('utf-8')
        )
        ciphertext_blob = response['CiphertextBlob']
        return base64.b64encode(ciphertext_blob).decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Failed to encrypt data with KMS: {e}")
        return None

def decrypt_data(ciphertext_b64):
    """Decrypt KMS-encrypted text from Base64 back to plaintext"""
    try:
        # Convert Base64 string back to binary blob
        ciphertext_blob = base64.b64decode(ciphertext_b64)
        # Request KMS to decrypt the blob
        response = kms_client.decrypt(CiphertextBlob=ciphertext_blob)
        # Return as readable string text
        return response['Plaintext'].decode('utf-8')
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        return "[Data could not be decrypted]"