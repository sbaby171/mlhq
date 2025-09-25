import os, sys, re, argparse, time, threading
from datetime import datetime 
import itertools
from mlhq import Client
DEFAULT_MODEL = "qwen/Qwen2.5-0.5B"
DEFAULT_MAX_NEW_TOKENS = 128

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
        header = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════╗
║                     🤖 AI CHAT TERMINAL                  ║
║                                                          ║
║              {Colors.BRIGHT_WHITE}Welcome to your AI Assistant{Colors.BRIGHT_CYAN}                ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(header)
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
    
    def run(self, max_new_tokens=DEFAULT_MAX_NEW_TOKENS):
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
    parser.add_argument('-b', '--backend', type=str, required=True)
    parser.add_argument('-m', '--model', type=str, default=DEFAULT_MODEL)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = __handle_cli_args()
    backend = args.backend
    model   = args.model


    if backend == "hflocal": 
        client = Client(backend=backend, model=model) 


    chat = TerminalChat()
    chat.run(max_new_tokens=args.max_new_tokens)
    

