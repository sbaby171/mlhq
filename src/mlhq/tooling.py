import importlib.util
from pathlib import Path


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
