import os
import re
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import texttospeech

# --- Configuration ---
SERVICE_ACCOUNT_KEY = "iam-key.json"
GCP_REGION = "us-central1"
MODEL_NAME = "gemini-2.5-flash" # Using a known stable model version

# --- Dynamic Project ID Loading ---
try:
    with open(SERVICE_ACCOUNT_KEY, 'r') as f:
        key_data = json.load(f)
    GCP_PROJECT_ID = key_data['project_id']
except FileNotFoundError:
    print(f"Error: Service account key file not found at '{SERVICE_ACCOUNT_KEY}'")
    exit(1)
except KeyError:
    print(f"Error: 'project_id' not found in '{SERVICE_ACCOUNT_KEY}'")
    exit(1)

# --- Set up authentication for all Google Cloud services ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_KEY

# --- Longer, fixed news story for comparison ---
NEWS_TEXT = (
    "海洋プラスチック問題に向けた画期的な新素材、静岡で開発。"
    "静岡県にある「未来環境研究所」は本日、植物由来の成分のみで作られた新しい生分解性プラスチック「アクアレス」を発表しました。"
    "この素材は、海水に触れると数ヶ��で自然に分解される特性を持っており、海洋汚染問題の解決に繋がるとして注目を集めています。"
    "開発チームを率いる田中博士によると、「アクアレス」は、海藻のゲル化成分に着想を得て、5年以上の歳月をかけて完成させました。"
    "製造プロセスにおいても、有害な化学物質を一切使用しないため、環境への負荷が極めて低いのが特徴です。"
    "この新素材は、特に食品包装や使い捨て容器への応用が期待されています。"
    "もし実用化されれば、現在世界的な課題となっている海洋プラスチックごみの削減に大きく貢献する可能性があります。"
    "研究所はすでに複数の国内メーカーと協力して試作品の生産を開始しており、来年には一部の製品で限定的な市場テストが行われる予定です。"
    "（このニュースは、テキスト読み上げのデモンストレーション用に作成された架空のものです。）"
)

def generate_ssml_with_ai(text):
    """
    Uses Vertex AI (with IAM auth) to intelligently add SSML tags.
    NOTE: This library is deprecated and will be removed after June 2026.
    """
    print("Generating SSML with Vertex AI...")
    try:
        vertexai.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        model = GenerativeModel(MODEL_NAME)

        prompt = f"""
        You are an expert in Speech Synthesis Markup Language (SSML) for Japanese news narration.
        Your task is to take the following plain Japanese text and convert it into a fully-formed SSML string, ready for a Text-to-Speech engine.
        Follow these rules precisely:
        1.  The entire output must be a single, valid SSML string. Start with `<speak>` and end with `</speak>`.
        2.  Do NOT include any other text, explanations, or markdown like ```ssml ... ```.
        3.  Use `<break time="600ms"/>` to create natural pauses after sentences.
        4.  Use `<emphasis level="moderate">` on important keywords or phrases to make them stand out.
        5.  Use the `<prosody>` tag to subtly vary the rate and pitch to make the speech sound more like a professional news anchor. The goal is a natural, engaging, and professional-sounding narration, not an over-dramatized one.
        Here is the text to convert:
        ---
        {text}
        ---
        """

        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```xml"):
            response_text = response_text[6:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        print("...AI generation complete.")
        return response_text.strip()
    except Exception as e:
        print(f"Error during Vertex AI API call: {e}")
        return f"<speak>{text}</speak>"

def auto_tag_ssml(text):
    """Applies simple, rule-based SSML tagging to plain text."""
    text = text.replace('。', '。<break time="600ms"/>')
    text = re.sub(r'「([^」]+)」', r'<emphasis level="moderate">「\1」</emphasis>', text)
    return f"<speak>{text}</speak>"

def synthesize_text(text, output_filename):
    """Synthesizes plain text with no tuning."""
    print(f"Generating default version: {output_filename}")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", name="ja-JP-Wavenet-D")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
    print("...Done.")

def synthesize_ssml(ssml, output_filename, speaking_rate=1.0, pitch=0.0):
    """Synthesizes SSML with optional global tuning."""
    print(f"Generating tuned SSML version: {output_filename}")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", name="ja-JP-Wavenet-D")
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
        pitch=pitch
    )
    
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    with open(output_filename, "wb") as out:
        out.write(response.audio_content)
    print("...Done.")

if __name__ == "__main__":
    print("--- Starting TTS Comparison Generation (with Vertex AI) ---")
    
    synthesize_text(NEWS_TEXT, "news_1_default.mp3")
    
    manual_ssml = f"""
    <speak>
        {NEWS_TEXT.replace('。', '。<break time="700ms"/>')}
    </speak>
    """
    synthesize_ssml(manual_ssml.strip(), "news_2_manual_tuned.mp3", speaking_rate=0.95, pitch=-1.0)
    
    auto_ssml = auto_tag_ssml(NEWS_TEXT)
    synthesize_ssml(auto_ssml, "news_3_auto_tagged.mp3")
    
    ai_ssml = generate_ssml_with_ai(NEWS_TEXT)
    print(f"\nVertex AI-generated SSML:\n{ai_ssml}\n")
    synthesize_ssml(ai_ssml, "news_4_ai_tuned.mp3")

    print("--- All files generated successfully. ---")