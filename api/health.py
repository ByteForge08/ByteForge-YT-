import json
from datetime import datetime

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'online',
            'service': 'ByteForgeYT',
            'timestamp': datetime.now().isoformat()
        })
    }