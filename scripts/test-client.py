from mlhq import Client
import argparse
import os
import json
from dotenv import load_dotenv
# ----------------------------------------------------------------------------:
def __handle_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend', type=str)
    parser.add_argument('-m', '--model', type=str)
    parser.add_argument('-c', '--config', type=str,)
    args = parser.parse_args()
    return args
# ----------------------------------------------------------------------------:
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
# ----------------------------------------------------------------------------:
def test_ollama_backend(config): 
    print("\nTesting Ollama Backend...") 
    client = Client(config=config)

    response = client.chat.completions.create(
        model=config["model"],
        messages=[{"role": "user", "content": "Say hello"}]
    ) 
    print(f"Response: {response}")

def test_hflocal_backend(model): 
    client = Client(backend="hflocal", model=model)
    print(client.text_generation("Tell me a joke?"))

if __name__ == "__main__":
     args = __handle_cli_args() 
     config_data = {}
     if args.config: 
         with open(args.config, "r") as f: 
             config_data = json.load(f)
     if config_data:
         if "backend" in config_data: 
              if config_data["backend"] == "ollama": 
                  test_ollama_backend(config=config_data) 
              elif config_data["backend"] == "openai": 
                  test_openai_backend(config=config_data)
              elif config_data["backend"] == "hflocal": 
                  test_hflocal_backend(config=config_data)

     #load_dotenv()
     #if args.backend == "openai": 
     #    test_openai_backend()
     #elif args.backend == "hflocal": 
     #    test_hflocal_backend(model= args.model)



