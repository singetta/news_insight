import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from crawlers import print_log

load_dotenv()


def get_instructions(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            instructions = file.read()
        return instructions
    except FileNotFoundError:
        print_log("File not found.")
    except Exception as e:
        print_log(f"An error occurred while reading the file: {e}")


def chat_request_news_insight(instruction_md_path, content_data, model_name='gpt-4o-mini'):
    if 'gpt' in model_name:
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key, timeout=30)
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "get_news_insight",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "news_insight": {"type": "string"},
                    },
                    "required": ["news_insight"],
                    "additionalProperties": False
                }
            }
        }
    elif 'deepseek' in model_name:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = "https://api.deepseek.com"
        client = OpenAI(api_key=api_key, base_url=base_url, timeout=60)
        response_format = {
            "type": "json_object"
        }
    else:
        raise Exception(f"Unsupported model: {model_name}")

    instructions = get_instructions(instruction_md_path)
    if not instructions:
        print_log("No instructions found.")
        return None

    message_list = [{
        "role": "system",
        "content": instructions
    }]
    if isinstance(content_data, list):
        for content in content_data:
            message_list.append({"role": "user", "content": content})
    else:
        message_list.append({"role": "user", "content": content_data})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=message_list,
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format=response_format,
            max_completion_tokens=4096,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print_log(f"An error occurred while making the request: {e}")
        return None
