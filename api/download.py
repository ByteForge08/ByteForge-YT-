import json

def handler(event, context):
    # Verificar se a função está sendo chamada
    print("DEBUG: Função download.py chamada!")
    print(f"Event: {json.dumps(event)}")
    
    query = event.get('queryStringParameters', {}) or {}
    url = query.get('url', '')
    path = event.get('path', '')
    
    # Resposta simples para teste
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        },
        'body': json.dumps({
            'success': True,
            'message': 'Função Python funcionando!',
            'url_recebida': url,
            'path': path,
            'status': 'online'
        })
    }
