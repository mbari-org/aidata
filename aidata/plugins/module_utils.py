import sys
import importlib.util


def load_module(module_name) -> object:
    """
    Find the module with the given name and return the path to it
    :param module_name: The name of the module
    """
    # Import the module dynamically and return it
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        if spec.loader is None:
            raise ImportError(f"Module {module_name} not found")
        spec.loader.exec_module(module)
        return module
    else:
        raise ImportError(f"Module {module_name} not found")
