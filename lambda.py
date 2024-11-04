import json
import boto3
import os
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = os.environ.get('BUCKET_NAME')

    # リクエストボディからファイル名とコンテンツタイプを取得
    body = json.loads(event['body'])
    file_name = body.get('file_name', str(uuid.uuid4()))
    content_type = body.get('content_type', 'application/octet-stream')

    key = f"{uuid.uuid4()}_{file_name}"

    expiration = 3600  # 1時間

    try:
        upload_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )

        download_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            ExpiresIn=expiration
        )

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
        logger.error(e)
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
