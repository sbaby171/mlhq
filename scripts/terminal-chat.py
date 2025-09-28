import os, sys, re, argparse, time, threading
from pyfiglet import Figlet
from datetime import datetime 
import itertools
import importlib.util
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


from mlhq import Client
from mlhq.logging_config import setup_logging, get_logger

DEFAULT_MODEL = "qwen/Qwen3-8B"
DEFAULT_MAX_NEW_TOKENS = 128
DEFAULT_TOOLS = "/Users/msbabo/code/mlhq/tools/weather_apis.py" 
def load_tools_from_file(file_path):
    """Load a Python file and return the module object."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Tools file not found: {file_path}")
    
    if not file_path.suffix == '.py':
        raise ValueError(f"File must be a Python file (.py): {file_path}")
    
    # Create a module spec from the file
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec from {file_path}")
    
    # Create and execute the module
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

class Colors:
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_BLUE = '\033[44m'
    BG_GREEN = '\033[42m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

class LoadingSpinner:
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None
        # Different spinner styles to choose from
        self.spinners = {
            'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
            'line': ['|', '/', '-', '\\'],
            'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
            'bounce': ['⠁', '⠂', '⠄', '⠂'],
            'pulse': ['●', '○', '●', '○']
        }
        self.current_spinner = self.spinners['dots']
    
    def _spin(self):
        spinner_cycle = itertools.cycle(self.current_spinner)
        while self.running:
            sys.stdout.write(f'\r{Colors.CYAN}{next(spinner_cycle)} {Colors.BRIGHT_WHITE}{self.message}...{Colors.RESET}')
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the spinner line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()


class TerminalChat:
    def __init__(self):
        self.chat_history = []
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        #header = f"""
#{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════╗
#║                     🤖 AI CHAT TERMINAL                  ║
#║                                                          ║
#║              {Colors.BRIGHT_WHITE}Welcome to your AI Assistant{Colors.BRIGHT_CYAN}                ║
#╚══════════════════════════════════════════════════════════╝{Colors.RESET}
#"""

        print("─" * 60)
        figlet = Figlet()
        print(figlet.renderText("MLHQ tChat"))
        #print(header)
        print(f"{Colors.DIM}Type 'quit', 'exit', or 'bye' to leave the chat{Colors.RESET}")
        print(f"{Colors.DIM}Type 'clear' to clear the chat history{Colors.RESET}")
        print("─" * 60)
    
    def print_user_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        print(f"\n{Colors.BRIGHT_GREEN}┌─ You {Colors.DIM}({timestamp}){Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}│{Colors.RESET} {message}")
        print(f"{Colors.BRIGHT_GREEN}└─{Colors.RESET}")
    
    def print_ai_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        print(f"\n{Colors.BRIGHT_BLUE}┌─ AI Assistant {Colors.DIM}({timestamp}){Colors.RESET}")
        
        # Simulate typing effect
        print(f"{Colors.BRIGHT_BLUE}│{Colors.RESET} ", end="", flush=True)
        for char in message:
            print(char, end="", flush=True)
            time.sleep(0.02)  # Adjust speed as needed
        
        print(f"\n{Colors.BRIGHT_BLUE}└─{Colors.RESET}")
    
    def get_user_input(self):
        prompt = f"\n{Colors.BRIGHT_YELLOW}▶ {Colors.BRIGHT_WHITE}"
        try:
            user_input = input(prompt).strip()
            print(Colors.RESET, end="")
            return user_input
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Chat interrupted. Goodbye!{Colors.RESET}")
            sys.exit(0)
    
    def simulate_ai_thinking(self):
        # Random delay to simulate processing
        thinking_time = time.time() % 3 + 1  # 1-4 seconds
        spinner = LoadingSpinner("AI is thinking")
        spinner.start()
        time.sleep(thinking_time)
        spinner.stop()
    
    def get_ai_response(self, user_message):
        # This is where you'd integrate with your actual AI
        # For demo purposes, here are some sample responses
        responses = [
            "That's an interesting question! I'd be happy to help you with that.",
            "I understand what you're asking. Let me think about the best way to approach this.",
            "Great question! Here's what I think about that topic.",
            "I see what you mean. That's definitely worth exploring further.",
            "Thanks for asking! I have some thoughts on this that might be helpful."
        ]
        
        # Simple response based on message length for demo
        import random
        return random.choice(responses) + f" (You said: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}')"
    
    def print_goodbye(self):
        goodbye = f"""
{Colors.BRIGHT_MAGENTA}╔══════════════════════════════════════════════════════════╗
║                    👋 Thanks for chatting!               ║
║                                                          ║
║                     See you next time!                   ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(goodbye)
    
    def run(self, client, max_new_tokens=DEFAULT_MAX_NEW_TOKENS):
        #self.clear_screen()
        self.print_header()
        
        while True:
            user_input = self.get_user_input()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                self.print_goodbye()
                break
            elif user_input.lower() == 'clear':
                self.clear_screen()
                self.print_header()
                continue
            elif not user_input:
                continue
            
            # Display user message
            self.print_user_message(user_input)
            
            # Show AI thinking
            self.simulate_ai_thinking()
            
            # Get and display AI response
            #ai_response = self.get_ai_response(user_input)
            # client.messages
            # messages = [
            #     "role":"system", "content": system_prompt,
            #     "role":"user", "content": prompt
            # ]
            ai_response = client.text_generation(user_input, max_new_tokens=max_new_tokens)
            self.print_ai_message(ai_response)
            
            # Store in history
            self.chat_history.append({
                'user': user_input,
                'ai': ai_response,
                'timestamp': datetime.now()
            })

def __handle_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--backend', type=str)
    parser.add_argument('-m', '--model', type=str, default=DEFAULT_MODEL)
    parser.add_argument('-t', '--tools', type=str, default=DEFAULT_TOOLS, help="Path to tools file (python)")
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("-c", "--config", type=str, help="MLHQ Client Config file", default={})
    parser.add_argument('--log-level', default='INFO',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        help='Set the logging level'
    )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = __handle_cli_args()
    backend = args.backend
    model   = args.model
    config = args.config
    tools = args.tools


    if tools: 
        tools_module = None 
        try:
            #if os.path.isdir(tools): # load all tools 
            tools_module = load_tools_from_file(tools)
            if hasattr(tools_module, 'TOOLS'):
                tools_list = tools_module.TOOLS
                print(f"Loaded {len(tools)} tools from {tools_list}")
                # Use with your tokenizer
                # tokenizer.apply_chat_template(messages, tools, ...)
            else:
                print("Warning: No 'TOOLS' attribute found in the module")
            # You can also access other functions/variables from the module
            # my_function = tools_module.my_function
        except Exception as e:
            print(f"Error loading tools file: {e}")
            sys.exit(1)

        print(f"Tools module: {tools_module}")
 
    sys.exit(1)

    setup_logging(args.log_level)
    logger = get_logger(__name__)
    logger.info(f"Starting terminal chat with log level: {args.log_level}")
    
    if config: 
        logger.info(f"Config path provided: {config}")
        client = Client(config=config) # Config to have system_prompt and tools?  

    elif backend == "hflocal": 
        client = Client(backend=backend, model=model) 

    chat = TerminalChat()
    chat.run(client=client, max_new_tokens=args.max_new_tokens)
    

