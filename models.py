
from pydantic import BaseModel

class ReviewOutput(BaseModel):
    approved: bool
    feedback: list[str]

from parameters import summarizer_temp, writer_temp, reviser_temp, reviewer_temp, translator_temp

##### THE GEMINI GANG #####
from langchain_google_genai import ChatGoogleGenerativeAI
models = [
    "gemma-3-27b-it", # CANNOT DO TOOLS AT ALL
    "gemini-2.5-flash-lite", # THIS BE A GOOD ONE MATEY
    "gemini-2.5-flash-preview-tts", # TOO LOW LIMITS
    "gemini-3-flash-preview", # **FUCKING 10/10 AMAZING** (A BIT LOW LIMIT)
    "gemini-flash-latest"
]
summarizer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=summarizer_temp)

writer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=writer_temp)

reviewer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=reviser_temp)
reviewer_agent = reviewer_agent.with_structured_output(ReviewOutput)

reviser_agent = ChatGoogleGenerativeAI(model=models[3], temperature=reviewer_temp)

translator_agent = ChatGoogleGenerativeAI(model=models[3], temperature=translator_temp)



##### THE DEEPINFRA GANG #####
from langchain_openai.chat_models.base import BaseChatOpenAI
#summarizer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=summarizer_temp)

#writer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=writer_temp)

#reviewer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', temperature=reviewer_temp)
#reviewer_agent = reviewer_agent.with_structured_output(ReviewOutput)

#reviser_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=reviser_temp)

#translator_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=translator_temp)

