import yaml
import tenpy

with open('settings/test.yml', 'r') as f:
    sim_params = yaml.safe_load(f)
tenpy.run_simulation(**sim_params)
