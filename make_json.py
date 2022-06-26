import json

d = {
    'English': {
        'name': 'English',
        'code_tesseract': 'eng',
        'code_deepl': 'en',
    },
    '日本語': {
        'name': '日本語',
        'code_tesseract': 'jpn',
        'code_deepl': 'ja',
    }
}

with open('./lang.json', mode='w', encoding='utf-8') as f:
    json.dump(d, f, indent=4, ensure_ascii=False)