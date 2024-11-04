import json
import boto3
import os
import logging
import uuid
from datetime import datetime, timedelta

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDBリソースとテーブルの設定
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('file_sharing_urls')

# S3クライアントの設定
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # 環境変数からバケット名を取得
    bucket_name = os.environ.get('BUCKET_NAME')
    
    # リクエストボディからファイル名とコンテンツタイプを取得
    try:
        body = json.loads(event['body'])
        file_name = body.get('file_name', str(uuid.uuid4()))
        content_type = body.get('content_type', 'application/octet-stream')
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid request body: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request body'}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            }
        }

    # ファイルのキーと有効期限の設定
    key = f"{uuid.uuid4()}_{file_name}"
    expiration = 3600  # 1時間
    expires_at = datetime.utcnow() + timedelta(seconds=expiration)

    try:
        # S3にアップロードするための事前署名付きURLの生成
        upload_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )

        # S3からダウンロードするための事前署名付きURLの生成
        download_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            ExpiresIn=expiration
        )

        # DynamoDBにURLと有効期限を保存
        table.put_item(
            Item={
                'url_id': str(uuid.uuid4()),
                'upload_url': upload_url,
                'download_url': download_url,
                'expires_at': expires_at.isoformat()  # ISOフォーマットで保存
            }
        )

        # 成功レスポンスの返却
        return {
            'statusCode': 200,
            'body': json.dumps({
                'upload_url': upload_url,
                'download_url': download_url,
                'key': key,
                'expires_in': expiration
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            }
        }
    except Exception as e:
        logger.error(f"Error generating URLs or saving to DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            }
        }
