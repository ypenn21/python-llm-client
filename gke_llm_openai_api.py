# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
# def query(payload, model_id, api_token):
# 	headers = {"Authorization": f"Bearer {api_token}"}
# 	API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
# 	response = requests.post(API_URL, headers=headers, json=payload)
# 	return response.json()
#
# model_id = "meta-llama/Llama-2-7b-chat-hf"
# api_token = "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" # get yours at hf.co/settings/tokens
# data = query("The goal of life is [MASK].", model_id, api_token)
#
# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
#
#
# # Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi(data)
#
# print("Completion result:", completion)

#https://docs.vllm.ai/en/latest/getting_started/quickstart.html
from openai import OpenAI
import time
import openai
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "ya29.a0AXooCgsEoqusUOAYf_II-k3GUZPg3gMNL_D0IkAIQRPWC2QmdpfGaAcLT6LGJUJJjIDxApBx9ZxbRP9sfhTupHB05JrbUIWg9duSUclf06pR3XkmJnPw0ktnUnAveF8ppOsteeSrq51UuHl2szD-w5Oqh4X16r-CRSRnrn4fm2C_aCgYKAX0SARISFQHGX2Mi2d4pZm4rkbYhcx2IQYV9rg0179"
openai_api_base = "http://34.36.61.140/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
start_time = time.time()  # Start timer
chat_response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    # model="meta-llama/Meta-Llama-3-8B-Instruct",
    # model="meta-llama/Llama-2-7b-hf",
    # model="google/gemma-2b",
    messages=[
        {"role": "system", "content": "Answer like an experienced literary professor; the output strictly wrapped in triple backquotes ```json```and strictly in JSON format;do not repeat quotes from the same book."},
        {"role": "user", "content": 'Please provide a quote from a random book, including book, quote and author. *Do not repeat quotes from same book, or author..'}
    ]
)
print("Chat response:", chat_response)
end_time = time.time()  # End timer
print(f"Time taken: {end_time - start_time} seconds")
# completion = client.completions.create(model="meta-llama/Meta-Llama-3-8B",
#                                       prompt="San Francisco is a")
# print("Completion result:", completion)
#
# end_time = time.time()  # End timer
#
# print(f"Time taken: {end_time - start_time} seconds")