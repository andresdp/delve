from plant_uml_renderer import PlantUMLGenerator
from src.model.model import rl_monitoring_adds_views

generator = PlantUMLGenerator(delete_gen_dir_during_init=False)
generator.object_model_renderer.name_break_length = 30
generator.object_model_renderer.left_to_right = True

generator.generate_object_models("rl_monitoring_adds", rl_monitoring_adds_views)