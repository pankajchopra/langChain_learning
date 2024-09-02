import asyncio
from tenacity import retry, wait_random_exponential
from app.tools.time_tools import time_taken
import vertexai
import vertexai.generative_models as generative_models
from vertexai.generative_models import GenerativeModel

from credentials_loader import get_google_credentials

import os

root_dir = os.getcwd()
print(root_dir)
# current_file_path = os.path.abspath(__file__)
# root_dir = os.path.dirname(current_file_path)
# print(root_dir)

if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None:
    # Load credentials
    credentials = get_google_credentials(None)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials
else:
    credentials = get_google_credentials(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))


# We will use the packages asyncio and tenacity to define an asynchronous version of the “generate” function,
# here’s the code:

@retry(wait=wait_random_exponential(multiplier=1, max=120))
@time_taken
async def async_generate(prompt):
    try:
        vertexai.init(project="gen-lang-client-0922515850", location="us-central1", credentials=credentials)
        model = GenerativeModel("gemini-1.5-flash-001")
        response = await model.generate_content_async(
            [prompt],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=False
        )
        response.prompt_feedback
        # print( "response.text", response.text)
        return response.text;
    except Exception as e:
        print(" An exception occurred: ", type(e).__name__, e)


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}


async def main():
    # to request all recipies in parallel
    # foodstuffs = ['haw herring', 'stroopwafels', 'hutspot', 'stamppot rauwe andijvie', 'zoute drop', 'poffertjes', 'bitterballen', 'oliebollen']
    # get_responses = [async_generate('give me a recipe for ' + f) for f in foodstuffs]
    # return await asyncio.gather(*get_responses)
    prompt = "In summary (two sentences) give me one step recipe of Butter Chicken, punjabi style"
    prompt_old = "in two sentence what are the major ingredients in a mint, should I add in all dishes  "
    return await async_generate(prompt)


if __name__ == "__main__":
    print(asyncio.run(main()));
