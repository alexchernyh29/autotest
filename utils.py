def create_curl_command(method, url, headers=None, json_data=None):
    """Генерирует строку curl на основе параметров запроса"""
    parts = [f"curl -X {method.upper()} '{url}'"]
    
    if headers:
        for key, value in headers.items():
            safe_value = value.replace("'", "'\"'\"'")
            parts.append(f"-H '{key}: {safe_value}'")
    
    if json_data:
        import json as json_module
        json_str = json_module.dumps(json_data, ensure_ascii=False, separators=(',', ':'))
        safe_json = json_str.replace("'", "'\"'\"'").replace('"', '\\"')
        parts.append(f"-d '{safe_json}'")
    
    return " ".join(parts)