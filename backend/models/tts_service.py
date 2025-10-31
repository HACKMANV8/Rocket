from gtts import gTTS
from deep_translator import GoogleTranslator
import base64
from io import BytesIO
from config import Config
import logging

logger = logging.getLogger(__name__)

class MultilingualTTS:
    # Map language codes to gTTS supported codes
    LANGUAGE_MAP = {
        'en': 'en',
        'es': 'es',
        'fr': 'fr',
        'de': 'de',
        'hi': 'hi',
        'zh': 'zh-cn',
        'ar': 'ar',
        'pt': 'pt'
    }
    
    @staticmethod
    def text_to_speech(text, language='en'):
        """
        Convert text to speech in multiple languages
        """
        try:
            if not text or not text.strip():
                return {"success": False, "error": "Empty text"}
            
            # Get gTTS language code
            gtts_lang = MultilingualTTS.LANGUAGE_MAP.get(language, 'en')
            
            # Translate if not English (only if translation service available)
            translated_text = text
            if language != 'en':
                try:
                    translator = GoogleTranslator(source='en', target=language)
                    translated_text = translator.translate(text)
                    logger.info(f"✅ Translated to {language}: {translated_text[:50]}...")
                except Exception as trans_error:
                    logger.warning(f"⚠️ Translation failed, using original text: {trans_error}")
                    translated_text = text  # Fallback to original
            
            # Generate speech with gTTS
            tts = gTTS(text=translated_text, lang=gtts_lang, slow=False)
            
            # Convert to base64
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
            
            logger.info(f"✅ Audio generated successfully for language: {language}")
            return {
                "success": True,
                "audio_base64": audio_base64,
                "language": language,
                "format": "mp3"
            }
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_supported_languages():
        """Return list of supported languages"""
        return Config.SUPPORTED_LANGUAGES