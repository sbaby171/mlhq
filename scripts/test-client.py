from mlhq import Client
import argparse
import os
from dotenv import load_dotenv

DEFAULT_MODEL = "qwen/Qwen2.5-0.5B"

def __handle_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend', type=str, required=True)
    parser.add_argument('-m', '--model', type=str, default=DEFAULT_MODEL)
    args = parser.parse_args()
    return args

def test_openai_backend(): 
    print("Testing OpenAI.responses.create API...")
    client = Client()
    response = client.responses.create(
        #model="gpt-5",
        model="gpt-4o",
        input="Write a one-sentence bedtime story about a unicorn."
    )
    print(response.output_text)
    print("Testing OpenAI.chat.completions.create API...")
    completion = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
           ]
    )
    print(completion.choices[0].message)

def test_hflocal_backend(model): 
    client = Client(backend="hflocal", model=model)

    print(client.text_generation("Tell me a joke?"))

if __name__ == "__main__":
     args = __handle_cli_args() 


     load_dotenv()
     if args.backend == "openai": 
         test_openai_backend()
 
     elif args.backend == "hflocal": 
         test_hflocal_backend(model= args.model)
