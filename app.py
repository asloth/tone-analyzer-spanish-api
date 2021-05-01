from flask import Flask
from flask import request
import json

from ibm_watson import ToneAnalyzerV3
from ibm_watson import LanguageTranslatorV3
from ibm_watson.tone_analyzer_v3 import ToneInput
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

authenticator_tone_analyzer = IAMAuthenticator('uzYhudZt4xOW91nTGCizqSAilFZ7XIB34BPCLRZpNQux')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator_tone_analyzer
)

authenticator_translator = IAMAuthenticator('JyYNpF3rt3CWlzYLdwKaISuuy4cnEofbXE4-V---M3E9')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator_translator
)

translator_url = 'https://api.us-south.language-translator.watson.cloud.ibm.com/instances/864f2320-8292-4973-a69e-f62cfa7303cb'
language_translator.set_service_url(translator_url)

tone_analyzer_url = 'https://api.us-south.tone-analyzer.watson.cloud.ibm.com/instances/d03cf30c-5bb9-45f9-b35d-f61f1d96c28a'
tone_analyzer.set_service_url(tone_analyzer_url)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bienvenidos a mi API "

@app.route("/ibm",methods=['POST'])
def api_ibm():
    values = request.get_json()
    translation = language_translator.translate(
        text=values['message'], 
        model_id='es-en').get_result()
    translated_text = translation['translations'][0]
    result = tone_analyzer.tone(tone_input=translated_text['translation'],
            content_type="text/plain").get_result()

    return json.dumps(result, indent=2)

if __name__ == "__main__":
    app.run()