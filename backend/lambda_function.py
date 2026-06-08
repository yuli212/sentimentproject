import json
import boto3
import uuid
from datetime import datetime

# Import custom modules created previously
import scraper
import analyzer

# Initialize connection to Amazon DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('SentimentHistory')

# KMS Key ID
KMS_KEY_ID = "arn:aws:kms:us-east-1:629478360569:key/a527c2a7-f3d8-4b86-be99-adfeaebc2c84"

def lambda_handler(event, context):
    """
    Main function that will be called by AWS Lambda when triggered by API Gateway.
    """
    # 1. Configure CORS 
    # Without this, browser will block your S3 web when calling this API.
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    try:
        # Capture route path and HTTP method from API Gateway
        http_method = event.get('httpMethod')
        path = event.get('path')

        # 2. Handle CORS Preflight Request
        if http_method == 'OPTIONS':
            return {"statusCode": 200, "headers": headers, "body": json.dumps("CORS OK")}

        # ROUTE 1: /get-news (Fetch News)
        if path == '/get-news' and http_method == 'GET':
            # Get keyword parameter from URL (e.g., /get-news?keyword=dollar)
            query_params = event.get('queryStringParameters') or {}
            keyword = query_params.get('keyword', 'dollar')
            
            # Call scraper.py module
            news_list = scraper.fetch_news(keyword, max_results=10) 
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Successfully fetched news",
                    "data": news_list
                })
            }

        # ROUTE 2: /analyze (VADER Analysis & Save to DB)
        elif path == '/analyze' and http_method == 'GET':
            query_params = event.get('queryStringParameters') or {}
            keyword = query_params.get('keyword', 'dollar')

            # 1. Fetch 10 news articles
            news_list = scraper.fetch_news(keyword, max_results=10)
            
            if not news_list:
                return {
                    "statusCode": 404,
                    "headers": headers,
                    "body": json.dumps({"error": "No news found."})
                }

            analysis_results = []

            # 2. Loop through each news article
            for news in news_list:
                news_title = news.get('title', '')
                news_summary = news.get('summary', '')
                news_link = news.get('link', '#')
                
                text_to_analyze = news_summary if news_summary else news_title
                
                # Process Analysis & Encryption
                ai_result = analyzer.analyze_sentiment(text_to_analyze)
                encrypted_text = analyzer.encrypt_data(text_to_analyze, KMS_KEY_ID)

                # Save to DynamoDB
                record_id = str(uuid.uuid4())
                table.put_item(
                    Item={
                        'RecordID': record_id,
                        'Timestamp': datetime.utcnow().isoformat(),
                        'Title': news_title,
                        'Sentiment': ai_result['sentiment'],
                        'Confidence': str(ai_result['confidence_score']),
                        'Encrypted_Text': encrypted_text or "ENCRYPTION_FAILED"
                    }
                )

                # Add to results list to send to web
                analysis_results.append({
                    "title": news_title,
                    "link": news_link,
                    "sentiment": ai_result['sentiment'],
                    "confidence": ai_result['confidence_score']
                })

            # 3. Return array/list containing 5 results
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Successfully analyzed 5 news articles",
                    "data": analysis_results
                })
            }

        # If route not found
        else:
            return {
                "statusCode": 404, 
                "headers": headers, 
                "body": json.dumps("API route not found.")
            }

    except Exception as e:
        print(f"[FATAL ERROR] {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "An internal server error occurred."})
        }