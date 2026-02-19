
from langchain.messages import SystemMessage
import system_messages
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from typing import cast
from pydantic import BaseModel


class ReviewOutput(BaseModel):
    approved: bool
    feedback: list[str]


##### THE GEMINI GANG #####
from langchain_google_genai import ChatGoogleGenerativeAI
models = [
    "gemma-3-27b-it", # CANNOT DO TOOLS AT ALL
    "gemini-2.5-flash-lite", # THIS BE A GOOD ONE MATEY
    "gemini-2.5-flash-preview-tts", # TOO LOW LIMITS
    "gemini-3-flash-preview", # **FUCKING 10/10 AMAZING** (A BIT LOW LIMIT)
    "gemini-flash-latest"
]
summarizer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=0.3)

writer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=0.6)

reviewer_agent = ChatGoogleGenerativeAI(model=models[3], temperature=0.4)
reviewer_agent = reviewer_agent.with_structured_output(ReviewOutput)

reviser_agent = ChatGoogleGenerativeAI(model=models[3], temperature=0.5)

translator_agent = ChatGoogleGenerativeAI(model=models[3], temperature=0.5)



##### THE DEEPINFRA GANG #####
from langchain_openai.chat_models.base import BaseChatOpenAI
#summarizer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=0.4)

#writer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=0.7)

#reviewer_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', temperature=0.4)
#reviewer_agent = reviewer_agent.with_structured_output(ReviewOutput)

#reviser_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=0.7)

#translator_agent = BaseChatOpenAI(model='deepseek-ai/DeepSeek-V3.2', base_url='https://api.deepinfra.com/v1/openai/', max_tokens=1024, temperature=0.5)



from time import sleep
from parameters import RATE_LIMIT_DELAY

def summarize_paper(filepath: str) -> str:

    """Summarize a scientific paper from a PDF or text file."""

    if filepath.endswith(".pdf"):
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        paper_text = "\n\n".join([page.page_content for page in pages])
    else:
        loader = TextLoader(filepath)
        docs = loader.load()
        paper_text = docs[0].page_content

    response = summarizer_agent.invoke([
        SystemMessage(content=system_messages.summarizer),
        {"role": "user", "content": paper_text}
    ])

    return str(response.content)

def write_article(paper_summary: str) -> str:

    """Write an engaging pop-science article from a scientific paper summary.
    Args:
        paper_summary: A summary of the scientific paper's key findings
    Returns:
        A complete pop-science article draft
    """

    response = writer_agent.invoke([
        SystemMessage(content=system_messages.writer),
        {"role": "user", "content": f"Please, write a pop-science article based on this summary:\n\n{paper_summary}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content)


def review_article(article: str) -> ReviewOutput:

    """Review a pop-science article for accessibility and engagement.
    Args:
        article: The article to review
    Returns:
        ReviewOutput with approved status and feedback list
    """

    response = reviewer_agent.invoke([
        SystemMessage(content=system_messages.reviewer),
        {"role": "user", "content": f"Please, review the following article:\n\n{article}"}
    ])
    sleep(RATE_LIMIT_DELAY)

    return cast(ReviewOutput, response)

def revise_article(article: str, feedback: str) -> str:

    """Revise an article based on editorial feedback.
    Args:
        article: The original article
        feedback: Review feedback with specific improvements needed
    Returns:
        An improved version of the article
    """

    response = reviser_agent.invoke([
        SystemMessage(content=system_messages.reviser),
        {"role": "user", "content": f"Original article:\n{article}\n\nReviewer's feedback:\n{feedback}\n\nPlease, revise the article."}
    ])
    sleep(RATE_LIMIT_DELAY)

    return str(response.content)


def save_article_english(article: str) -> str:

    """Save the finalized article to a file.
    Args:
        article: The complete finalized article text
    Returns:
        Confirmation message with file path
    """

    filepath = f"/home/fj/eve/final_article_english.md"
    with open(filepath, 'w') as f:
        f.write(article)

    return filepath


def translate_article(article: str) -> str:

    """Translate the finalized article to czech.
    Args:
        article: The finalized article
    Returns:
        The translated article
    """

    response = translator_agent.invoke([
        SystemMessage(content=system_messages.translator),
        {"role": "user", "content": f"Please, translate the following article to Czech:\n\n{article}"}
    ])

    return str(response.content)


def save_article_czech(article: str) -> str:

    """Save the finalized and translated article to a file.
    Args:
        article: The complete finalized and translated article text
    Returns:
        Confirmation message with file path
    """

    filepath = f"/home/fj/eve/final_article_czech.md"
    with open(filepath, 'w') as f:
        f.write(article)

    return filepath