
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from parameters import MAX_REVISIONS, PAPER_PATH
from dotenv import load_dotenv


load_dotenv()


# define the graph state
class ArticleState(TypedDict):
    paper_path: str
    original_text: str
    summary: str
    current_article: str
    feedback: str
    revision_count: int
    approved: bool
    translated_article: str
    llm_calls: int
    article_english_path: str
    article_czech_path: str


# define graph nodes
def extract_node(state:ArticleState):
    from tools import extract_text
    paper_text = extract_text(filepath=state["paper_path"])

    print(f"EXTRACT SUCCESS")
    write_to_file(
        filename="extract_node_output.txt",
        content=paper_text
        )
    
    return {
        "original_text": paper_text,
    }


def summarize_node(state: ArticleState):
    from tools import summarize_paper
    summary = summarize_paper(paper_text=state["original_text"])

    print(f"SUMMARIZE SUCCES")
    write_to_file(
        filename="summarize_node_output.txt",
        content=summary
        )

    return {
        "summary": summary,
        "llm_calls": state["llm_calls"] + 1
        }


def write_node(state: ArticleState):
    from tools import write_article
    article = write_article(paper_summary=state["summary"])

    print(f"WRITE SUCCESS")
    write_to_file(
        filename="write_node_output.txt",
        content=article
        )

    return {
        "current_article": article,
        "revision_count": 0,
        "llm_calls": state["llm_calls"] + 1
        }


def review_node(state: ArticleState):
    from tools import review_article
    response = review_article(article=state["current_article"], original_text=state["original_text"])

    print(f"REVIEW SUCCESS, REVISION: {state['revision_count']}, APPROVED: {response.approved}")
    write_to_file(
        filename=f"review_node_output_{state['revision_count']}.txt",
        content="\n".join(response.feedback)
        )
    return {
        "feedback": "\n".join(response.feedback),
        "approved": response.approved,
        "llm_calls": state["llm_calls"] + 1
    }


def revise_node(state: ArticleState):
    from tools import revise_article
    revised = revise_article(
        article=state["current_article"],
        feedback=state["feedback"]
        )
    
    print(f"REVISION SUCCESS")
    write_to_file(
        filename=f"revise_node_output_{state['revision_count']}.txt",
        content=revised
        )
    return {
        "current_article": revised,
        "revision_count": state["revision_count"] + 1,
        "llm_calls": state["llm_calls"] + 1
    }


def save_english_node(state: ArticleState):
    from tools import save_article_english
    result = save_article_english(article=state["current_article"])

    print(f"SAVE_ENGLISH SUCCESS")
    write_to_file(
        filename="save_english_node_output.txt",
        content=result
    )
    return {"article_english_path": result}


def translate_node(state: ArticleState):
    from tools import translate_article
    translated = translate_article(article=state["current_article"])

    print(f"TRANSLATE SUCCESS")
    write_to_file(
        filename="translate_node_output.txt",
        content=translated
    )
    return {
        "translated_article": translated,
        "llm_calls": state["llm_calls"] + 1
        }


def save_czech_node(state: ArticleState):
    from tools import save_article_czech
    result = save_article_czech(article=state["translated_article"])

    print(f"SAVE_CZECH SUCCESS")
    write_to_file(
        filename="save_czech_node_output.txt",
        content=result
    )
    return {"article_czech_path": result}


# conditional edge function
def should_revise(state: ArticleState) -> Literal["revise", "save_english"]:
    """Decide whether to revise or save"""
    if state["approved"]:
        return "save_english"
    elif state["revision_count"] >= MAX_REVISIONS:
        # Max revisions reached, save anyway
        return "save_english"
    else:
        return "revise"



# assemble the graph
workflow = StateGraph(ArticleState)

# nodes
workflow.add_node("extract", extract_node)
workflow.add_node("summarize", summarize_node)
workflow.add_node("write", write_node)
workflow.add_node("review", review_node)
workflow.add_node("revise", revise_node)
workflow.add_node("save_english", save_english_node)
workflow.add_node("translate", translate_node)
workflow.add_node("save_czech", save_czech_node)

# the flow
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "summarize")
workflow.add_edge("summarize", "write")
workflow.add_edge("write", "review")
workflow.add_conditional_edges("review", should_revise)
workflow.add_edge("revise", "review")
workflow.add_edge("save_english", "translate")
workflow.add_edge("translate", "save_czech")
workflow.add_edge("save_czech", END)

agent = workflow.compile()


# make a picture
graph_image = agent.get_graph(xray=True).draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(graph_image)

from tools import write_to_file, clear_state_outputs_txt


# invoke
if __name__ == "__main__":
    clear_state_outputs_txt()
    result = agent.invoke({
        "paper_path": PAPER_PATH,
        "original_text": "",
        "summary": "",
        "current_article": "",
        "feedback": "",
        "revision_count": 0,
        "approved": False,
        "translated_article": "",
        "llm_calls": 0,
        "article_english_path": "",
        "article_czech_path": ""
    })
    
    print("Final article:", result["current_article"][:200], "...")
    print("Approved:", result["approved"])
    print("Revisions made:", result["revision_count"])
    print("Total LLM calls:", result["llm_calls"])