from __future__ import annotations                                                                                                        
from typing import Any, Optional, Dict 
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer




from .base import Backend
#from mlhq.logging_config import get_logger
from mlhq.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)



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

    def text_generation(self, prompt, **kwargs):                                
        if "stop" in kwargs:                                                    
            kwargs["stop_strings"] = kwargs["stop"]                             
            del kwargs["stop"]                                                  
        logger.debug(f"Text-generation kwargs: {kwargs}")                   
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)    
        #print(f"DEBUG: Tokenized Input: {inputs}")
        gen_kwargs = {                                                          
            "input_ids": inputs.input_ids,                                      
            "attention_mask": inputs.attention_mask,                            
            "tokenizer": self.tokenizer                                         
        }                                                                       
        kwargs.update(gen_kwargs)                                               
        response = self.model.generate(**kwargs)                                
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
