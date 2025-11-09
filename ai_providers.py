from typing import Optional, Dict, Any
import openai
import google.generativeai as genai
from anthropic import Anthropic
from groq import Groq
import httpx
from abc import ABC, abstractmethod
import deepl


class AIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str, 
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """Translate text using the AI provider"""
        pass
    
    def _parse_translation_with_terms(self, result: str) -> Dict:
        """Parse translation and extract terms from AI response"""
        import json
        import re
        
        # Try to extract translation and terms
        translation = result
        terms = {}
        
        try:
            # Look for TRANSLATION: and TERMS: markers
            if "TRANSLATION:" in result and "TERMS:" in result:
                parts = result.split("TERMS:")
                translation = parts[0].replace("TRANSLATION:", "").strip()
                
                # Extract JSON from markdown code block or plain JSON
                terms_text = parts[1]
                json_match = re.search(r'```json\s*(.*?)\s*```', terms_text, re.DOTALL)
                if json_match:
                    terms_json = json_match.group(1)
                    terms = json.loads(terms_json)
                else:
                    # Try to find JSON directly
                    json_match = re.search(r'\{.*\}', terms_text, re.DOTALL)
                    if json_match:
                        terms = json.loads(json_match.group(0))
        except Exception as e:
            print(f"Warning: Could not parse terms from AI response: {e}")
            # If parsing fails, just use the full text as translation
            pass
        
        return {
            "translation": translation,
            "terms": terms
        }
    
    def _build_translation_prompt(self, text: str, source_lang: str, 
                                  target_lang: str, glossary: Dict[str, str] = None,
                                  context: str = None, extract_terms: bool = False) -> str:
        """Build a comprehensive translation prompt"""
        prompt = f"""You are a professional novel translator. Translate the following text from {source_lang} to {target_lang}.

IMPORTANT GUIDELINES:
- Maintain the narrative style and tone of the original text
- Preserve character emotions and dialogue nuances
- Keep the text natural and fluent in {target_lang}
- DO NOT add explanations or notes
- DO NOT translate sound effects literally - adapt them culturally
- Maintain paragraph structure
"""
        
        if glossary and len(glossary) > 0:
            prompt += "\nTERMINOLOGY (Use these exact translations for consistency):\n"
            for original, translation in glossary.items():
                prompt += f"- {original} = {translation}\n"
        
        if context:
            prompt += f"\nPREVIOUS CONTEXT:\n{context}\n"
        
        prompt += f"\nTEXT TO TRANSLATE:\n{text}\n\nTRANSLATION:"
        
        if extract_terms:
            prompt += """

AFTER THE TRANSLATION, please identify and list important terms in JSON format:
- Character names (people, important figures)
- Location names (places, cities, realms)
- Special terms (abilities, skills, techniques, magic)
- Important items (artifacts, weapons, special objects)
- Organizations/Groups (guilds, clans, factions)

Format: 
TRANSLATION: [your translation here]

TERMS:
```json
{
  "character": [{"original": "name", "translation": "çeviri"}],
  "location": [{"original": "place", "translation": "çeviri"}],
  "skill": [{"original": "ability", "translation": "çeviri"}],
  "item": [{"original": "object", "translation": "çeviri"}],
  "organization": [{"original": "group", "translation": "çeviri"}]
}
```
"""
        
        return prompt


class OpenAIProvider(AIProvider):
    """OpenAI (ChatGPT) Provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = openai.OpenAI(api_key=api_key)
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional novel translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            result = response.choices[0].message.content.strip()
            
            if extract_terms:
                return self._parse_translation_with_terms(result)
            return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"OpenAI translation error: {str(e)}")


class GeminiProvider(AIProvider):
    """Google Gemini Provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    'temperature': self.config.get('temperature', 0.7),
                    'max_output_tokens': self.config.get('max_tokens', 4000),
                }
            )
            result = response.text.strip()
            
            if extract_terms:
                return self._parse_translation_with_terms(result)
            return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"Gemini translation error: {str(e)}")


class ClaudeProvider(AIProvider):
    """Anthropic Claude Provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = Anthropic(api_key=api_key)
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.get('max_tokens', 4000),
                temperature=self.config.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            result = response.content[0].text.strip()
            
            if extract_terms:
                return self._parse_translation_with_terms(result)
            return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"Claude translation error: {str(e)}")


class GroqProvider(AIProvider):
    """Groq Provider"""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = Groq(api_key=api_key)
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional novel translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 4000)
            )
            result = response.choices[0].message.content.strip()
            
            if extract_terms:
                return self._parse_translation_with_terms(result)
            return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"Groq translation error: {str(e)}")


class DeepSeekProvider(AIProvider):
    """DeepSeek Provider"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key
        self.base_url = kwargs.get('base_url', 'https://api.deepseek.com/v1')
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a professional novel translator."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": self.config.get('temperature', 0.7),
                        "max_tokens": self.config.get('max_tokens', 4000)
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                result_json = response.json()
                result = result_json['choices'][0]['message']['content'].strip()
                
                if extract_terms:
                    return self._parse_translation_with_terms(result)
                return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"DeepSeek translation error: {str(e)}")


class PerplexityProvider(AIProvider):
    """Perplexity AI Provider"""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-sonar-large-128k-online", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        prompt = self._build_translation_prompt(text, source_lang, target_lang, glossary, context, extract_terms)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a professional novel translator."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": self.config.get('temperature', 0.7),
                        "max_tokens": self.config.get('max_tokens', 4000)
                    },
                    timeout=120.0
                )
                response.raise_for_status()
                result_json = response.json()
                result = result_json['choices'][0]['message']['content'].strip()
                
                if extract_terms:
                    return self._parse_translation_with_terms(result)
                return {"translation": result, "terms": {}}
        except Exception as e:
            raise Exception(f"Perplexity translation error: {str(e)}")


class DeepLProvider(AIProvider):
    """DeepL Professional Translation Provider"""
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.translator = deepl.Translator(api_key)
        self.is_pro = kwargs.get('is_pro', False)
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """
        DeepL translation - Note: DeepL is a specialized translation service,
        not a general AI. It won't extract terms like AI models do.
        """
        
        try:
            # Map language codes to DeepL format
            lang_map = {
                'en': 'EN',
                'tr': 'TR',
                'de': 'DE',
                'fr': 'FR',
                'es': 'ES',
                'ja': 'JA',
                'zh': 'ZH',
                'ko': 'KO'
            }
            
            source = lang_map.get(source_lang, source_lang.upper())
            target = lang_map.get(target_lang, target_lang.upper())
            
            # DeepL translation
            result = self.translator.translate_text(
                text,
                source_lang=source if source != 'AUTO' else None,
                target_lang=target,
                formality='default',
                preserve_formatting=True
            )
            
            translated_text = result.text
            
            # If glossary terms exist, do post-processing replacement
            if glossary:
                for original, translation in glossary.items():
                    # Case-insensitive replacement while preserving case
                    import re
                    pattern = re.compile(re.escape(original), re.IGNORECASE)
                    translated_text = pattern.sub(translation, translated_text)
            
            # DeepL doesn't extract terms, so we return empty terms
            # But we can do basic name extraction
            extracted_terms = {}
            if extract_terms:
                # Basic extraction (capitalized words)
                import re
                names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
                if names:
                    # Find their translations
                    extracted_terms = {
                        'character': [
                            {'original': name, 'translation': name}  # DeepL already translated
                            for name in set(names[:10])  # Limit to 10
                        ]
                    }
            
            return {
                "translation": translated_text,
                "terms": extracted_terms
            }
            
        except Exception as e:
            raise Exception(f"DeepL translation error: {str(e)}")


class GoogleCloudTranslateProvider(AIProvider):
    """Google Cloud Translation API Provider"""
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """Google Cloud Translation API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    params={'key': self.api_key},
                    json={
                        'q': text,
                        'source': source_lang,
                        'target': target_lang,
                        'format': 'text'
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                translated_text = result['data']['translations'][0]['translatedText']
                
                # Apply glossary if provided
                if glossary:
                    for original, translation in glossary.items():
                        import re
                        pattern = re.compile(re.escape(original), re.IGNORECASE)
                        translated_text = pattern.sub(translation, translated_text)
                
                return {
                    "translation": translated_text,
                    "terms": {}
                }
                
        except Exception as e:
            raise Exception(f"Google Cloud Translate error: {str(e)}")


class MicrosoftTranslatorProvider(AIProvider):
    """Microsoft Azure Translator Provider"""
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key
        self.region = kwargs.get('region', 'global')
        self.base_url = "https://api.cognitive.microsofttranslator.com"
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """Microsoft Translator API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/translate",
                    params={
                        'api-version': '3.0',
                        'from': source_lang,
                        'to': target_lang
                    },
                    headers={
                        'Ocp-Apim-Subscription-Key': self.api_key,
                        'Ocp-Apim-Subscription-Region': self.region,
                        'Content-Type': 'application/json'
                    },
                    json=[{'text': text}],
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                translated_text = result[0]['translations'][0]['text']
                
                # Apply glossary
                if glossary:
                    for original, translation in glossary.items():
                        import re
                        pattern = re.compile(re.escape(original), re.IGNORECASE)
                        translated_text = pattern.sub(translation, translated_text)
                
                return {
                    "translation": translated_text,
                    "terms": {}
                }
                
        except Exception as e:
            raise Exception(f"Microsoft Translator error: {str(e)}")


class LibreTranslateProvider(AIProvider):
    """LibreTranslate - Open Source Translation Provider"""
    
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key or "", model, **kwargs)
        self.base_url = kwargs.get('base_url', 'https://libretranslate.com')
        self.api_key = api_key  # Optional for public instance
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """LibreTranslate API (Free & Open Source)"""
        
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    'q': text,
                    'source': source_lang,
                    'target': target_lang,
                    'format': 'text'
                }
                
                if self.api_key:
                    data['api_key'] = self.api_key
                
                response = await client.post(
                    f"{self.base_url}/translate",
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                translated_text = result['translatedText']
                
                # Apply glossary
                if glossary:
                    for original, translation in glossary.items():
                        import re
                        pattern = re.compile(re.escape(original), re.IGNORECASE)
                        translated_text = pattern.sub(translation, translated_text)
                
                return {
                    "translation": translated_text,
                    "terms": {}
                }
                
        except Exception as e:
            raise Exception(f"LibreTranslate error: {str(e)}")


class MyMemoryProvider(AIProvider):
    """MyMemory Translation - World's Largest Translation Memory"""
    
    def __init__(self, api_key: str = None, model: str = None, **kwargs):
        super().__init__(api_key or "", model, **kwargs)
        self.base_url = "https://api.mymemory.translated.net"
        self.email = kwargs.get('email', '')  # Optional email for higher limits
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """MyMemory Translation API (Free tier available)"""
        
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    'q': text,
                    'langpair': f'{source_lang}|{target_lang}'
                }
                
                if self.email:
                    params['de'] = self.email
                
                response = await client.get(
                    f"{self.base_url}/get",
                    params=params,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get('responseStatus') != 200:
                    raise Exception(f"API returned error: {result.get('responseDetails', 'Unknown error')}")
                
                translated_text = result['responseData']['translatedText']
                
                # Apply glossary
                if glossary:
                    for original, translation in glossary.items():
                        import re
                        pattern = re.compile(re.escape(original), re.IGNORECASE)
                        translated_text = pattern.sub(translation, translated_text)
                
                return {
                    "translation": translated_text,
                    "terms": {}
                }
                
        except Exception as e:
            raise Exception(f"MyMemory translation error: {str(e)}")


class YandexTranslateProvider(AIProvider):
    """Yandex Translate Provider"""
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.api_key = api_key
        self.folder_id = kwargs.get('folder_id', '')
        self.base_url = "https://translate.api.cloud.yandex.net/translate/v2"
    
    async def translate(self, text: str, source_lang: str, target_lang: str,
                       glossary: Dict[str, str] = None, context: str = None, extract_terms: bool = False) -> Dict:
        """Yandex Translate API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers={
                        'Authorization': f'Api-Key {self.api_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'texts': [text],
                        'targetLanguageCode': target_lang,
                        'sourceLanguageCode': source_lang,
                        'folderId': self.folder_id
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                translated_text = result['translations'][0]['text']
                
                # Apply glossary
                if glossary:
                    for original, translation in glossary.items():
                        import re
                        pattern = re.compile(re.escape(original), re.IGNORECASE)
                        translated_text = pattern.sub(translation, translated_text)
                
                return {
                    "translation": translated_text,
                    "terms": {}
                }
                
        except Exception as e:
            raise Exception(f"Yandex Translate error: {str(e)}")


# Provider Factory
class AIProviderFactory:
    """Factory to create AI provider instances"""
    
    PROVIDERS = {
        'openai': OpenAIProvider,
        'chatgpt': OpenAIProvider,
        'gemini': GeminiProvider,
        'claude': ClaudeProvider,
        'groq': GroqProvider,
        'deepseek': DeepSeekProvider,
        'perplexity': PerplexityProvider,
        'deepl': DeepLProvider,
        'google-translate': GoogleCloudTranslateProvider,
        'microsoft-translator': MicrosoftTranslatorProvider,
        'libretranslate': LibreTranslateProvider,
        'mymemory': MyMemoryProvider,
        'yandex': YandexTranslateProvider,
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, api_key: str, 
                       model: str = None, **kwargs) -> AIProvider:
        """Create an AI provider instance"""
        provider_name = provider_name.lower()
        
        if provider_name not in cls.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(cls.PROVIDERS.keys())}")
        
        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(api_key=api_key, model=model, **kwargs)
    
    @classmethod
    def get_available_providers(cls):
        """Get list of available providers"""
        return list(cls.PROVIDERS.keys())

