import json
import math
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
    # Allow frontrend to access API without CORS error
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }

    try:
        # Capture route path and HTTP method from API Gateway
        http_method = event.get('httpMethod')
        path = event.get('path')

        # 2. Handle CORS request
        if http_method == 'OPTIONS':
            return {"statusCode": 200, "headers": headers, "body": json.dumps("CORS OK")}

        # Step 1: /get-news (Fetch News)
        if path == '/get-news' and http_method == 'GET':
            # Get keyword parameter from URL 
            query_params = event.get('queryStringParameters') or {}
            keyword = query_params.get('keyword', 'dollar')
            
            # Call scraper.py
            news_list = scraper.fetch_news(keyword, max_results=10) 
            
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Successfully fetched news",
                    "data": news_list
                })
            }

        # Step 2: /analyze (Analyze Sentiment + Save to DynamoDB)
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
                
                # Execute sentiment analysis and encryption
                ai_result = analyzer.analyze_sentiment(text_to_analyze)
                encrypted_text = analyzer.encrypt_data(text_to_analyze, KMS_KEY_ID)

                # Save to DynamoDB
                record_id = str(uuid.uuid4())
                try:
                    table.put_item(
                        Item={
                            'RecordID': record_id,
                            'Timestamp': datetime.utcnow().isoformat(),
                            'Keyword': str(keyword),  # Save search keyword
                            'Title': str(news_title),
                            'Date': str(news.get('date', 'Unknown release time')),  # Save publication date
                            'Sentiment': str(ai_result['sentiment']),
                            'Confidence': str(ai_result['confidence_score']),
                            'Encrypted_Text': encrypted_text or "ENCRYPTION_FAILED"
                        }
                    )
                except Exception as db_error:
                    print(f"[WARNING] Failed to save record to DynamoDB: {db_error}")
                    # Loop will continue to next news even if fails

                # Add to results list to send to web
                analysis_results.append({
                    "title": news_title,
                    "link": news_link,
                    "date": news.get('date', 'Unknown release time'),
                    "sentiment": ai_result['sentiment'],
                    "confidence": ai_result['confidence_score']
                })

            # 3. Return array/list containing results
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": f"Successfully analyzed {len(analysis_results)} news articles",  # Dynamic message
                    "data": analysis_results
                })
            }

        # Step 3: /history (Fetch past analysis records from DynamoDB)
        elif path == '/history' and http_method == 'GET':
            try:
                query_params = event.get('queryStringParameters') or {}
                page = max(1, int(query_params.get('page', 1)))
                limit = min(max(1, int(query_params.get('limit', 20))), 50)

                # Full table scan — follow LastEvaluatedKey to get all records
                items = []
                scan_response = table.scan()
                items.extend(scan_response.get('Items', []))
                while 'LastEvaluatedKey' in scan_response:
                    scan_response = table.scan(ExclusiveStartKey=scan_response['LastEvaluatedKey'])
                    items.extend(scan_response.get('Items', []))

                # Sort by Timestamp descending (newest first)
                items.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)

                total_records = len(items)
                total_pages = math.ceil(total_records / limit) if total_records > 0 else 1

                # Slice only the records needed for this page
                start = (page - 1) * limit
                page_items = items[start:start + limit]

                # Decrypt only the page slice — avoids KMS timeout on large datasets
                history_data = []
                for item in page_items:
                    if 'Encrypted_Text' in item:
                        item['Plain_Text'] = analyzer.decrypt_data(item['Encrypted_Text'])
                        del item['Encrypted_Text']
                    history_data.append(item)

                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps({
                        "message": f"Fetched {len(history_data)} of {total_records} records",
                        "data": history_data,
                        "pagination": {
                            "page": page,
                            "limit": limit,
                            "totalRecords": total_records,
                            "totalPages": total_pages
                        }
                    })
                }
            except Exception as db_error:
                print(f"[ERROR] Failed to fetch history from DynamoDB: {db_error}")
                return {
                    "statusCode": 500,
                    "headers": headers,
                    "body": json.dumps({"error": "Failed to retrieve history."})
                }

        # if route not found, return 404
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