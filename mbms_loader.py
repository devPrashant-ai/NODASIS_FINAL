# mbms_loader.py

import os
import importlib.util

def load_all_models(model_dir="models/mbms"):
    """
    Dynamically loads all .py MBMS model files in the given folder.
Returns a dict of model_name → module
    """
    model_dict = {}

    for filename in os.listdir(model_dir):
        if filename.endswith(".py"):
            model_path = os.path.join(model_dir, filename)
            module_name = filename[:-3]

            spec = importlib.util.spec_from_file_location(module_name, model_path)
            module = importlib.util.module_from_spec(spec)

            try:
                spec.loader.exec_module(module)
                model_dict[module_name] = module
            except Exception as e:
                print(f"❌ Failed to load {module_name}: {e}")

    print(f"✅ Loaded {len(model_dict)} MBMS models.")
    return model_dict
