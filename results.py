import os
import numpy as np
import importlib.util
import pandas as pd
import sys

data_folder = 'Data'
results_folder = 'Results'
num_iterations = 1000


csv_files = [file for file in os.listdir(data_folder) if file.endswith('.csv')]


functions = {
    'csgoswiss': {'module': 'csgoswiss', 'seeded': False},
    'roundrobin': {'module': 'roundrobin', 'seeded': False},
    'swiss': {'module': 'swiss', 'seeded': False},
    'multistage': {'module': 'multistage', 'seeded': False},
    'dualtournament': {'module': 'dualtournament', 'seeded': False}
    #add others as necessary
}

os.makedirs(results_folder, exist_ok=True)


for func_name, function_data in functions.items():
    func_results = []


    for csv_file in csv_files:
        file_path = os.path.join(data_folder, csv_file)

        dataframe = pd.read_csv(file_path)


        module_spec = importlib.util.spec_from_file_location(function_data['module'], f"{function_data['module']}.py")
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        for _ in range(num_iterations):
            func = getattr(module, func_name)
            result = func(dataframe, function_data['seeded'])
            func_results.append(result)


    additional_param_str = str(functions[func_name]['seeded']).lower()
    output_filename = f"{func_name}_{additional_param_str}.npy"
    output_path = os.path.join(results_folder, output_filename)
    np.save(output_path, np.array(func_results))
