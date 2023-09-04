from gym.envs.registration import register
import os
import fileinput

FD = os.path.dirname(os.path.realpath(__file__));
Eplus_path='/usr/local/EnergyPlus-9-6-0/'

register(
    id='5Zone-96-Default-v0',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':Eplus_path, # The EnergyPlus software path
            'weather_path':FD + '/envs/weather/pittsburgh_TMY3.epw', # The epw weather file
            'bcvtb_path':FD + '/envs/bcvtb/', # The BCVTB path
            'variable_path':FD + '/envs/eplus_models/5_zone_9_6_T_M/variables_Default.cfg', # The cfg file
            'idf_path':FD + '/envs/eplus_models/5_zone_9_6_T_M/5Zone_Default_T_m.idf', # The idf file
            'env_name': '5Zone-96-Default-v0',
            });

register(
    id='5Zone-96-Control-v0',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':Eplus_path, # The EnergyPlus software path
            'weather_path':FD + '/envs/weather/pittsburgh_TMY3.epw', # The epw weather file
            'bcvtb_path':FD + '/envs/bcvtb/', # The BCVTB path
            'variable_path':FD + '/envs/eplus_models/5_zone_9_6_T_M/variables_Control.cfg', # The cfg file
            'idf_path':FD + '/envs/eplus_models/5_zone_9_6_T_M/5Zone_Control_T_m.idf', # The idf file
            'env_name': '5Zone-96--Control-v0',
            });

register(
    id='Lab-Building-default-v0',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':Eplus_path, # The EnergyPlus software path
            'weather_path':FD + '/envs/weather/pittsburgh_TMY3.epw', # The epw weather file
            'bcvtb_path':FD + '/envs/bcvtb/', # The BCVTB path
            'variable_path':FD + '/envs/eplus_models/lab_building/variables_Default.cfg', # The cfg file
            'idf_path':FD + '/envs/eplus_models/lab_building/lab_building_external.idf', # The idf file
            'env_name': 'Lab-Building-default-v0',
            });

register(
    id='idf-non-ottimizzato-v0',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':Eplus_path, # The EnergyPlus software path
            'weather_path':FD + '/envs/weather/IKASTR4-hour.epw', # The epw weather file
            'bcvtb_path':FD + '/envs/bcvtb/', # The BCVTB path
            'variable_path':FD + '/envs/eplus_models/lab_building/variables_Default.cfg', # The cfg file
            'idf_path':FD + '/envs/eplus_models/lab_building/idf_non_ottimizzato_SENSORI_control_external.idf', # The idf file
            'env_name': 'idf-non-ottimizzato-v0',
            });

register(
    id='idf-ottimizzato-v0',
    entry_point='eplus_env.envs:EplusEnv',
    kwargs={'eplus_path':Eplus_path, # The EnergyPlus software path
            'weather_path':FD + '/envs/weather/IKASTR4-hour.epw', # The epw weather file
            'bcvtb_path':FD + '/envs/bcvtb/', # The BCVTB path
            'variable_path':FD + '/envs/eplus_models/lab_building/variables_Default.cfg', # The cfg file
            'idf_path':FD + '/envs/eplus_models/lab_building/idf_ottimizzato_SENSORI_control_external.idf', # The idf file
            'env_name': 'idf-ottimizzato-v0',
            });
