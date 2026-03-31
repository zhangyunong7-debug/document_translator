"""
Translation engine implementations
"""
import re
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class TranslationEngine(ABC):
    """Abstract base class for translation engines"""

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the engine is properly configured with API keys"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of the engine"""
        pass

    def translate_batch(self, texts: List[str], source_lang: str, target_lang: str) -> List[str]:
        """Translate multiple texts, with default implementation using single translation"""
        return [self.translate(text, source_lang, target_lang) for text in texts]


class GoogleTranslateEngine(TranslationEngine):
    """Google Translate API implementation"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.api_url = "https://translation.googleapis.com/language/translate/v2"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_name(self) -> str:
        return "Google Translate"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text

        try:
            import requests
            params = {
                'key': self.api_key,
                'q': text,
                'source': source_lang if source_lang != 'auto' else None,
                'target': target_lang,
                'format': 'text'
            }
            if source_lang == 'auto':
                params.pop('source', None)

            response = requests.post(self.api_url, data=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'data' in result and 'translations' in result['data']:
                return result['data']['translations'][0]['translatedText']
            return text
        except Exception as e:
            raise Exception(f"Google Translate error: {str(e)}")


class DeepLEngine(TranslationEngine):
    """DeepL API implementation"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.api_url = "https://api-free.deepl.com/v2/translate"  # Free tier
        self.pro_url = "https://api.deepl.com/v2/translate"  # Pro tier

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_name(self) -> str:
        return "DeepL"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text

        try:
            import requests

            # Determine API URL based on API key format
            url = self.pro_url if self.api_key.endswith(":fx") else self.api_url

            headers = {
                'Authorization': f'DeepL-Auth-Key {self.api_key}'
            }

            data = {
                'text': text,
                'target_lang': target_lang.upper()
            }

            if source_lang != 'auto':
                data['source_lang'] = source_lang.upper()

            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'translations' in result and len(result['translations']) > 0:
                return result['translations'][0]['text']
            return text
        except Exception as e:
            raise Exception(f"DeepL error: {str(e)}")


class BaiduTranslateEngine(TranslationEngine):
    """Baidu Translate API implementation"""

    def __init__(self, app_id: str = "", api_key: str = ""):
        self.app_id = app_id
        self.api_key = api_key
        self.api_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def is_configured(self) -> bool:
        return bool(self.app_id and self.api_key)

    def get_name(self) -> str:
        return "百度翻译"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text

        try:
            import hashlib
            import random
            import urllib.parse
            import requests

            salt = str(random.randint(32768, 65536))
            sign_str = f"{self.app_id}{text}{salt}{self.api_key}"
            sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

            params = {
                'q': text,
                'from': source_lang if source_lang != 'auto' else 'auto',
                'to': target_lang,
                'appid': self.app_id,
                'salt': salt,
                'sign': sign
            }

            response = requests.post(self.api_url, data=params, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'trans_result' in result and len(result['trans_result']) > 0:
                return ''.join([item['dst'] for item in result['trans_result']])
            return text
        except Exception as e:
            raise Exception(f"百度翻译 error: {str(e)}")


class GoogleFreeEngine(TranslationEngine):
    """Google Translate free version (using deep-translator)"""

    def __init__(self):
        self.engine = None

    def is_configured(self) -> bool:
        return True  # Always available

    def get_name(self) -> str:
        return "Google Translate (免费)"

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not text.strip():
            return text

        try:
            from deep_translator import GoogleTranslator

            lang_map = {
                'auto': 'auto',
                'zh-CN': 'zh-CN',
                'en': 'en',
                'ja': 'ja',
                'ko': 'ko',
                'fr': 'fr',
                'de': 'de',
                'es': 'es',
                'ru': 'ru',
                'pt': 'pt',
                'it': 'it',
                'ar': 'ar',
                'th': 'th',
                'vi': 'vi'
            }

            src = lang_map.get(source_lang, 'auto')
            tgt = lang_map.get(target_lang, 'zh-CN')

            translator = GoogleTranslator(source=src, target=tgt)
            result = translator.translate(text)

            return result if result else text
        except Exception as e:
            raise Exception(f"Google Translate (免费) error: {str(e)}")


def get_available_engines(config: 'Config') -> Dict[str, TranslationEngine]:
    """Get all available translation engines based on configuration"""
    engines = {
        "google_free": GoogleFreeEngine(),
        "google": GoogleTranslateEngine(config.get("google_api_key", "")),
        "deepl": DeepLEngine(config.get("deepl_api_key", "")),
        "baidu": BaiduTranslateEngine(
            config.get("baidu_app_id", ""),
            config.get("baidu_api_key", "")
        )
    }
    return engines


def get_engine(engine_id: str, config: 'Config') -> Optional[TranslationEngine]:
    """Get a specific translation engine"""
    engines = get_available_engines(config)
    return engines.get(engine_id)


# Supported languages mapping
SUPPORTED_LANGUAGES = {
    "auto": "自动检测",
    "zh-CN": "中文(简体)",
    "zh-TW": "中文(繁体)",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "pt": "葡萄牙语",
    "it": "意大利语",
    "ar": "阿拉伯语",
    "th": "泰语",
    "vi": "越南语",
    "id": "印尼语",
    "ms": "马来语",
    "tr": "土耳其语",
    "pl": "波兰语",
    "nl": "荷兰语",
    "hi": "印地语"
}
