import ollama
import subprocess
import json
import os
from ddgs import DDGS

def url_search(url: str) -> str:
    try:
        return json.dumps(DDGS().extract(url, "text_rich"))
    except Exception as e:
        return str(e)
def news_search(search_query: str) -> str:
    try:
        return json.dumps(DDGS().text(search_query, max_results=5))
    except Exception as e:
        return str(e)

def internet_search(search_query: str) -> str:
    try:
        return json.dumps(DDGS().text(search_query, max_results=5))
    except Exception as e:
        return str(e)

# 1. Define the actual tool function
def execute_shell_command(command: str) -> str:
    """Executes a terminal command and returns stdout or stderr."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        print(f"🔧 >[Showing Tool result ] {result.stdout}")
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)
# 2. Map tool names to Python functions
TOOL_MAP = {
    'execute_shell_command': execute_shell_command,
    'internet_search': internet_search,
    'news_search': news_search,
    'url_search': url_search
}
# 3. Provide schema representations for Ollama
TOOLS_SCHEMA = [
    {
        'type': 'function',
        'function': {
            'name': 'execute_shell_command',
            'description': 'Execute safe terminal shell commands on the local machine.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'command': {
                        'type': 'string',
                        'description': 'The exact bash or shell command to run.',
                    }
                },
                'required': ['command'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'internet_search',
            'description': 'Execute duckduckgo search general knowledge',
            'parameters': {
                'type': 'object',
                'properties': {
                    'search_query': {
                        'type': 'string',
                        'description': 'The exact text to search',
                    }
                },
                'required': ['search_query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'news_search',
            'description': 'Execute duckduckgo search for news, latest events',
            'parameters': {
                'type': 'object',
                'properties': {
                    'search_query': {
                        'type': 'string',
                        'description': 'The exact text to search',
                    }
                },
                'required': ['search_query'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'url_search',
            'description': 'Execute a url/source fetch and/or search. It needs to have the https://',
            'parameters': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'The exact text to search',
                    }
                },
                'required': ['url'],
            },
        },
    }
] 

def main():
    llm = os.environ['LLM']
    print("=== Local Terminal agent (type 'exit' to leave) ===")
    messages = [
        {"role": "system", "content": "You are a helpful local CLI assistant. You can inspect the system and run tasks using your tools."}
    ]

    while True:
        user_input = input("\n😁 > ")
        if user_input.lower() in ["exit"]:
            break

        messages.append({"role": "user", "content": user_input})

        # Chamada ao modelo local via Ollama
        response = ollama.chat(
            model=llm,
            messages=messages,
            tools=TOOLS_SCHEMA
        )
        while response.get('message', {}).get('tool_calls'):
            messages.append(response['message'])
            
            for tool_call in response['message']['tool_calls']:
                tool_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                
                print(f"🔧 >[Executing Tool] {tool_name}({json.dumps(arguments)})")
                if tool_name == "execute_shell_command":
                    user_input = input("\n😁 Approve? ")
                    if user_input.lower() in ["no"]:
                        messages.append({
                            "role": "user",
                            "content": "Command is wrong or not approved",
                        })
                        break
                if tool_name in TOOL_MAP:
                    # Execute tool and grab output string
                    tool_result = TOOL_MAP[tool_name](**arguments)
                    
                    # Provide tool outcome back to the model context
                    messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_result
                    })
                else:
                    print(f"⚠️ >Unknown tool execution attempted: {tool_name}")
            
            # Re-submit history including tool logs for final evaluation
            response = ollama.chat(
                model=llm,
                messages=messages,
                tools=TOOLS_SCHEMA
            )
        assistant_message = response['message']
        print(f"Agent 🤖> {assistant_message['content']}")
        messages.append(assistant_message)

if __name__ == "__main__":
    main()
