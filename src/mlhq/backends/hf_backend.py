from __future__ import annotations                                                                                                        
from typing import Any, Optional, Dict 
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import json 

from .base import Backend
from mlhq.logging_config import get_logger
logger = get_logger(__name__)

def get_current_temperature(location: str, unit: str = "celsius"):
    """Get current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, and the unit in a dict
    """
    return {
        "temperature": 26.1,
        "location": location,
        "unit": unit,
    }


def get_temperature_date(location: str, date: str, unit: str = "celsius"):
    """Get temperature at a location and date.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        date: The date to get the temperature for, in the format "Year-Month-Day".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, the date and the unit in a dict
    """
    return {
        "temperature": 25.9,
        "location": location,
        "date": date,
        "unit": unit,
    }


def get_function_by_name(name):
    if name == "get_current_temperature":
        return get_current_temperature
    if name == "get_temperature_date":
        return get_temperature_date

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_date",
            "description": "Get temperature at a location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the temperature for, in the format "Year-Month-Day".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]
MESSAGES = [
    {"role": "user",  "content": "What's the temperature in San Francisco now? How about tomorrow? Current Date: 2024-09-30."},
]

class HFLocalClient:                                                            
    def __init__(self, model_name, api_key=""): 
        logger.debug("Initializing HuggingFace backend")
        #self.logger = logging.getLogger(f"{__name__}.HFLocalClient")            
        #self.logger.info(f"Initializing HFLocalClient with model_name={model_name}")
        print(f"Initializing HFLocalClient with model_name={model_name}")
        self.model_name = model_name                                            
        self.tokenizer = AutoTokenizer.from_pretrained(model_name,local_files_only=True) 
        self.model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True) 
                                                                                
        if torch.cuda.is_available():                                           
            self.device = "cuda"                                                
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            self.device = "mps"                                                 
        else:                                                                   
            self.device = "cpu"                                                 
                                                                                
        self.model = self.model.to(self.device)                                 
        #self.logger.info(f"Using device={self.device}")       
        print(f"Using device={self.device}")       


    # NOTE: Because the tools has is separately provided to the appy_chat_template
    # we need to pass it in as a separate arg here. 
    def text_generation(self, messages, tools=[], **kwargs):   

        if "stop" in kwargs:                                                    
            kwargs["stop_strings"] = kwargs["stop"]                             
            del kwargs["stop"]                                                  
        logger.debug(f"Text-generation kwargs: {kwargs}")                   

        #inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)    
        #inputs = self.tokenizer([inputs], return_tensors="pt")
        #inputs = self.tokenizer.apply_chat_template(
        #    messages,
        #    tools = tools, 
        #    tokenize=False,
        #    add_generation_prompt=True
        #).to(self.device)
        inputs = tokenizer.apply_chat_template(                                         
            messages,                                                               
            tools = tools, 
            add_generation_prompt=True,                                             
            tokenize=True,                                                          
            return_dict=True,                                                       
            return_tensors="pt",                                                    
        ).to(self.device)

        #gen_kwargs = {                                                          
        #    "input_ids": inputs.input_ids.to("mps"),  
        #    "attention_mask": inputs.attention_mask,                            
        #    "tokenizer": self.tokenizer                                         
        #}                                                                       
        #kwargs.update(gen_kwargs)

        response = self.model.generate(**inputs, **kwargs) 
        #self.logger.info(f"Incoming/Outgoing text: {self.tokenizer.decode(response[0])}")
        return self.tokenizer.decode(response[0][inputs.input_ids.shape[1]:-1]) 



class HFLocalBackend(Backend):                                                   
    def __init__(                                                               
        self,                                                                   
        *,                                                                      
        api_key: Optional[str] = None,                                          
        base_url: Optional[str] = None,                                         
        organization: Optional[str] = None,                                     
        project: Optional[str] = None,                                          
        model,
        **extra: Any,                                                           
    ) -> None:                                                                  
        self._inner = HFLocalClient(                                                   
            api_key=api_key,                                                    
            #base_url=base_url,                                                  
            #organization=organization,                                          
            #project=project,                                                    
            model_name = model, 
        )                                                                       
        #self._responses = _OpenAIResponses(self._inner)                         
        #self._chat = _OpenAIChat(self._inner)
        #self._text_generation = self._inner.text_generation

    @property                                                                   
    def text_generation(self):  
        return self._inner.text_generation                                                  
                                                                                
    #@property                                                                   
    #def chat(self) -> ChatAPI:                                                  
    #    return self._chat 
