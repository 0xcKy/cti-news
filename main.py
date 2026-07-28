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
    """Update news from database, from unread to read."""
    print('Update Unread News Tool Called')
    update_table_news()

@tool("list_unread_news", description="Query for unread news. Use this tool when prompted to show and/or list unread news articles.")
def get_unread_news():
    """Get unread news articles."""
    print('Get Unread News Tool Called')
    result = get_table_news()
    return raw_llm.invoke(result).content

@tool("download_rss_feeds", description="Download new articles from RSS feeds. Use this when prompted to download and/or update news articles", return_direct = True)
def download_rss_feeds():
    """Download RSS feed news articles."""
    print('Download RSS feed tool called')
    get_rss()

@tool("write_rss_report", description="Write a HTML report based on downloaded RSS feeds. Use this tool when prompted to write or create a report from RSS feeds and/or news articles", return_direct = True)
def write_rss_report():
    """Write reports in HTML format using RSS feeds and/or news articles"""
    write_rss_html()
    print("Report generated from RSS feeds!")

llm = init_chat_model(CHAT_MODEL, model_provider='ollama', temperature=0)
llm = llm.bind_tools([update_unread_news, get_unread_news, download_rss_feeds, write_rss_report])

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
