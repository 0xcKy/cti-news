import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from pg_test import get_table_news, update_table_news

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

load_dotenv()

CHAT_MODEL = 'llama3.2:3b'


class ChatState(TypedDict):
    messages: list

@tool
def update_unread_news():
    """Update news from database, from unread to read. Return only text confirming tool execution."""
    print('Update Unread News Tool Called')
    update_table_news()

@tool
def get_unread_news():
    """Get news articles from table, provided by database. If asked, show information like title, URL, content without change."""
    print('Get Unread News Tool Called')
    result = get_table_news()
    return raw_llm.invoke(result).content

llm = init_chat_model(CHAT_MODEL, model_provider='ollama')
llm = llm.bind_tools([update_unread_news, get_unread_news])
raw_llm = init_chat_model(CHAT_MODEL, model_provider='ollama')

def llm_node(state):
    response = llm.invoke(state['messages'])
    return {'messages': state['messages'] + [response]}


def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message, 'tool_calls', None) else 'end'

tool_node = ToolNode([update_unread_news, get_unread_news])

def tools_node(state):
    result = tool_node.invoke(state)

    return {
        'messages': state['messages'] + result['messages']
    }

builder = StateGraph(ChatState)
builder.add_node('llm', llm_node)
builder.add_node('tools', tools_node)
builder.add_edge(START, 'llm')
builder.add_edge('tools', 'llm')
builder.add_conditional_edges('llm', router, {'tools': 'tools', 'end': END})

graph = builder.compile()


if __name__ == '__main__':
    state = {'messages': []}

    print('Type an instruction or "quit".\n')

    while True:
        user_message = input('> ')

        if user_message.lower() == 'quit':
            break

        state['messages'].append({'role': 'user', 'content': user_message})

        state = graph.invoke(state)

        print(state['messages'][-1].content, '\n')
