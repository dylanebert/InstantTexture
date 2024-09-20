from instant_texture import Converter


input_mesh_path = "inputs/chair.obj"
output_mesh_path = "outputs/chair.glb"

converter = Converter()
converter.convert(input_mesh_path, output_mesh_path)
