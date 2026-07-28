import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from pg import get_table_news, update_table_news, download_table_news
from feed import get_rss, write_rss_html

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

load_dotenv()

CHAT_MODEL = 'llama3.2:3b'


class ChatState(TypedDict):
    messages: list

@tool("update_article_state", description="Mark news articles from unread to read. Use this when prompted to update and/or mark news articles from unread to read.")
def update_unread_news():
    """
    Purpose:
        Mark one or more unread cybersecurity news articles as read.

    Use this tool when:
        - The user explicitly asks to mark news as read.
        - The user confirms that specific news should no longer appear as unread.
        - The user requests to mark all unread news as read.

    Do NOT use this tool when:
        - The user is only requesting to list, summarize or analyze news.
        - The user has not explicitly requested or confirmed the update.
        - The news to update cannot be uniquely identified.

    Returns:
        A confirmation indicating whether the requested articles were successfully updated.

    Important:
        - Never infer which articles should be marked as read.
        - If the user refers to "all news", update every unread article.
        - If the request is ambiguous (for example, "mark that one as read" without a clear reference), do not call this tool and ask for clarification.
        - If no articles were updated, inform the user that no changes were made and do not retry the tool."""
    update_table_news()

@tool("list_unread_news", description="Query for unread news. Use this tool when prompted to show and/or list unread news articles.")
def get_unread_news():
    """
    Purpose:
        Retrieve all unread cybersecurity news available in the knowledge base.

    Use this tool when:
        - The user asks to list unread or new cybersecurity news.
        - The user requests the latest collected news that have not yet been reviewed.
        - The user asks to summarize, analyze or search within unread news.
        - The user requests information that depends on the content of unread news.

    Do NOT use this tool when:
        - The user wants to mark news as read.
        - The user asks only about news that have already been marked as read.
        - The request is unrelated to the stored cybersecurity news.

    Returns:
        A collection of all unread news. Each item contains:
        - Title
        - URL
        - Published date
        - Collected date
        - Source
        - Content
    """
    result = get_table_news()
    return raw_llm.invoke(result).content

@tool("download_rss_feeds", description="Download new articles from RSS feeds. Use this when prompted to download and/or update news articles")
def download_rss_feeds():
    """
    Purpose:
        Download newly published cybersecurity news from all configured RSS feeds and store only articles that are not already present in the knowledge base.

    Use this tool when:
        - The user asks to check for new cybersecurity news.
        - The user requests to update, refresh or synchronize the news database.
        - The user wants the latest news available from the configured RSS feeds.

    Do NOT use this tool when:
        - The user asks to list, summarize or analyze stored news.
        - The user requests information that can be answered using the existing news database.
        - The user asks to mark news as read.
    """
    print('Download RSS feed tool called')
    get_rss()

@tool("write_rss_report", description="Write a HTML report based on downloaded RSS feeds. Use this tool when prompted to write or create a report from RSS feeds and/or news articles")
def write_rss_report():
        """
    Purpose:
        Generate an HTML report containing cybersecurity news from the RSS feed knowledge base.

    Use this tool when:
        - The user requests an HTML report.
        - The user asks to generate, create or export a news report.
        - The user wants the collected news formatted as an HTML document for sharing, archiving or viewing.

    Do NOT use this tool when:
        - The user only wants to list, summarize or analyze news.
        - The user asks questions that can be answered directly from the stored news.
        - The user requests to update the RSS feeds.
        - The user requests to mark news as read.
    """
    write_rss_html()
    print("Report generated from RSS feeds!")

llm = init_chat_model(CHAT_MODEL, model_provider='ollama', temperature=0)
llm = llm.bind_tools([update_unread_news, get_unread_news, download_rss_feeds, write_rss_report])
raw_llm = init_chat_model(CHAT_MODEL, model_provider='ollama', temperature=0)

def llm_node(state):
    response = None

    for chunk in llm.stream(state["messages"]):
        if response is None:
            response = chunk
        else:
            response += chunk

        if chunk.content:
            print(chunk.content, end="", flush=True)

    print()

    return {
        "messages": state["messages"] + [response]
    }

def router(state):
    last_message = state['messages'][-1]
    if getattr(last_message, 'tool_calls', None):
        return 'tools' 
    else:
        return 'end'
    

def router_end(state):
    last_message = state['messages'][-1]
    if getattr(last_message, 'name', None) in ['write_rss_report','download_rss_feeds']:
        return 'end' 
    else:
        return 'llm'

tool_node = ToolNode([update_unread_news, get_unread_news, download_rss_feeds, write_rss_report])

def tools_node(state):
    result = tool_node.invoke(state)

    return {
        'messages': state['messages'] + result['messages']
    }

builder = StateGraph(ChatState)
builder.add_node('llm', llm_node)
builder.add_node('tools', tools_node)
builder.add_edge(START, 'llm')
#builder.add_edge('tools', 'llm')
builder.add_conditional_edges('tools', router_end, {'llm': 'llm', 'end': END})
builder.add_conditional_edges('llm', router, {'tools': 'tools', 'end': END})

graph = builder.compile()


if __name__ == '__main__':
    state = {'messages': []}

    print('Type an instruction or "quit".')

    while True:
        user_message = input('\n> ')

        if user_message.lower() == 'quit':
            break

        state['messages'].append({'role': 'user', 'content': user_message})

        state = graph.invoke(state)
