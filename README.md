# InstantTexture

A minimalist Python library for converting vertex-colored .obj meshes to uv-mapped, textured .glb meshes.

## Installation

1. **Clone the repository**

```bash
    git clone https://github.com/dylanebert/InstantTexture.git
    cd InstantTexture
```

2. **Set up a virtual environment (optional)**

```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install the package locally**

```bash
    pip install -e .
```

## Usage

A simple usage example is provided in the `examples/convert.py` file.

```python
from instant_texture import Converter


input_mesh_path = "inputs/chair.obj"
output_mesh_path = "outputs/chair.glb"

converter = Converter()
converter.convert(input_mesh_path, output_mesh_path)
```

## Walkthrough

For a complete walkthrough of the process, see the [walkthrough notebook](https://githubtocolab.com/dylanebert/InstantTexture/blob/main/notebooks/walkthrough.ipynb).

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- [trimesh](https://github.com/mikedh/trimesh)
- [xatlas](https://github.com/jpcy/xatlas)
- [opencv](https://github.com/opencv/opencv)
- [Pillow](https://github.com/python-pillow/Pillow)
