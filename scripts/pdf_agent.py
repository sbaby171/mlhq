import sys 
from textwrap import dedent 
from mlhq import Client
from mlhq.tooling import load_tools_from_file
import re
import json
# ----------------------------------------------------------------------------:
def extract_all_tool_calls(text):
    """Extract all tool_call sections from the text."""
    pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    tool_calls = []
    for match in matches:
        try:
            tool_call_data = json.loads(match.strip())
            tool_calls.append(tool_call_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            tool_calls.append(match.strip())  # Keep raw content if parsing fails
    
    return tool_calls
# ----------------------------------------------------------------------------:


# Configuration stuff
pdf_path = "/Users/msbabo/Downloads/ReAct.pdf"
config = "/Users/msbabo/code/mlhq/scripts/configs/hflocal_Qwen3_8B__basic.json"
tools_file = "/Users/msbabo/code/mlhq/tools/pdf_apis.py"
# Prompts 
sys_p = dedent("You are and agent that helps users work and analyze PDFs.")
prompt = f"Can you convert this PDF to markdown: '{pdf_path}'?"
# Generation args
temperature = 0.6
max_new_tokens = 512

# ----------------------------------------------------------------------------:
tools_list = None                                                           
tools_module = None                                                         
try:                                                                    
    tools_module = load_tools_from_file(tools_file)  
    if hasattr(tools_module, 'TOOLS'):                                  
        tools_list = tools_module.TOOLS                                 
        print(f"Loaded {len(tools_list)} tools from {tools_list}")           
    else:                                                               
        print("Warning: No 'TOOLS' attribute found in the module")      
except Exception as e:                                                  
    print(f"Error loading tools file: {e}")                             
    sys.exit(1)                                                         
print(f"Tools module: {tools_module}")
# ----------------------------------------------------------------------------:
messages = [
    {"role":"system", "content": sys_p},
    {"role":"user", "content": prompt}
]

# ----------------------------------------------------------------------------:
client = Client(config=config)
response = client.text_generation(
    messages=messages,
    tools = tools_list,
    temperature = temperature,
    max_new_tokens = max_new_tokens
)
print(response)

func_list = extract_all_tool_calls(response)
print(f"Function list: {func_list}")
for func in func_list: 
    #Function list: [{'name': 'parse_pdf_to_md', 'arguments': {'pdf_path': '/Users/msbabo/Downloads/ReAct.pdf'}}]
    fresp = tools_module.get_function_by_name(func['name'])(**func['arguments'])
    print(fresp)
