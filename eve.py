
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
    llm_calls: int
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
    from tools import write_article_czech
    article = write_article_czech(paper_summary=state["summary"], original_text=state["original_text"])

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
        original_text=state["original_text"],
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


def save_article_node(state: ArticleState):
    from tools import save_article
    result = save_article(article=state["current_article"])

    print(f"SAVE_ENGLISH SUCCESS")
    write_to_file(
        filename="save_article_node_output.txt",
        content=result
    )
    return {"article_czech_path": result}


# conditional edge function -> save or revise the article?
def should_revise(state: ArticleState) -> Literal["revise", "save"]:
    """Decide whether to revise or save"""
    if state["approved"]:
        return "save"
    elif state["revision_count"] >= MAX_REVISIONS:
        # Max revisions reached, save anyway
        return "save"
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
workflow.add_node("save", save_article_node)

# the flow
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "summarize")
workflow.add_edge("summarize", "write")
workflow.add_edge("write", "review")
workflow.add_conditional_edges("review", should_revise)
workflow.add_edge("revise", "review")
workflow.add_edge("save", END)

agent = workflow.compile()


# make a picture
graph_image = agent.get_graph(xray=True).draw_mermaid_png()
with open("agent_graph.png", "wb") as f:
    f.write(graph_image)


# invoke
from tools import write_to_file, clear_state_outputs_txt

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
        "llm_calls": 0,
        "article_czech_path": ""
    })
    
    print("Final article:", result["current_article"][:200], "...")
    print("Approved:", result["approved"])
    print("Revisions made:", result["revision_count"])
    print("Total LLM calls:", result["llm_calls"])