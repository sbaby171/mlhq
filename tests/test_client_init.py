import re
import pytest

from mlhq import Client
from mlhq.client import ClientConfig  #


def test_default_init_values():
    c = Client()
    cfg = c.config
    assert isinstance(cfg, ClientConfig)
    assert cfg.api_key is None
    assert cfg.endpoint == "https://api.example.com"
    assert cfg.timeout == 30.0

def openai_sanity_check(): 
    client = Client()

    response = client.responses.create(
        #model="gpt-5",
        model="gpt-4o",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)
