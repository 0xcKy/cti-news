import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from pg_test import get_table_info 

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END

load_dotenv()

CHAT_MODEL = 'llama3.2:3b'


class ChatState(TypedDict):
    messages: list

@tool
def list_unread_news():
    """Return a bullet list of every UNREAD news Title, URL and UUID"""
    print('List Unread News Tool Called')
    result = ""
    with open('news.json') as f:
        d = json.load(f)
        for i in d:
            if i["status"] == "unread":
                result = result + f"--> {i["title"]} ==== {i["publishedAt"]} \n\n{i["summary"]}\n\nURL: {i["url"]}\nUUID: {i["uid"]}\n\n"
        return result


@tool
def get_information_from_table():
    """Get news articles from table, provided by database. Summarize all news article given. Return a short summary of the articles separated individually content in plain text"""
    print('Get table information tool called')
    result = get_table_info()
    return raw_llm.invoke(result).content


@tool
def summarize_news(uid):
    """Summarize all news article given. Return a short summary of the articles separated individually content in plain text."""
    print('Summarize Web Article Tool Called')

    with open('news.json') as f:
        d = json.load(f)
        prompt = "Summarize this news article concisely:\n\n"
        for i in d:
            prompt = prompt + (
                f"Title: {i["title"]}\n"
                f"Published At: {i["publishedAt"]}\n"
                f"Summary: {i["summary"]}\n"
                f"URL: {i["url"]}\n"
            )

        return raw_llm.invoke(prompt).content

llm = init_chat_model(CHAT_MODEL, model_provider='ollama')
llm = llm.bind_tools([list_unread_news, summarize_news, get_information_from_table])

raw_llm = init_chat_model(CHAT_MODEL, model_provider='ollama')

def llm_node(state):
    response = llm.invoke(state['messages'])
    return {'messages': state['messages'] + [response]}


def router(state):
    last_message = state['messages'][-1]
    return 'tools' if getattr(last_message, 'tool_calls', None) else 'end'



tool_node = ToolNode([list_unread_news, summarize_news, get_information_from_table])


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
