# Import the Speech-to-Text client library
import os
from app.llm.credentials_loader import get_google_credentials
from google.cloud import speech


def audio_process(audio_stream, chataudio_args):
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None:
        # Load credentials
        credentials = get_google_credentials(None)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials
    else:
        credentials = get_google_credentials(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))

    with open('audio.wav', 'wb') as f:
        f.write(audio_stream)

    with open('audio.wav', 'rb') as f:
        audio_content = f.read()

    response = run_speech_to_text(audio_content, chataudio_args)
    return response


def run_speech_to_text(audio_content, chataudio_args) -> speech.RecognizeResponse:
    # Instantiates a client

    client = speech.SpeechClient()
    print('client initiated', client)

    audio = speech.RecognitionAudio(content=audio_content)  # content=file.read() for PCM encoding
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,  # default WEBM_OPUS
        sample_rate_hertz=chataudio_args.sample_rate,  # default(48000)
        language_code="en-US",
        model="default",
        audio_channel_count=chataudio_args.channel_count,
    )

    response = client.recognize(config=config, audio=audio)

    # logic to handle multiple transcripts in one conversation
    transcript_builder = []

    for result in response.results:
        transcript_builder.append(f"{result.alternatives[0].transcript}")
        transcript_builder.append(f"\nConfidence: {result.alternatives[0].confidence}")
    transcript = "".join(transcript_builder)

    return transcript
