import cv2
import numpy as np
import trimesh
import xatlas
from PIL import Image, ImageFilter
from pathlib import Path
import warnings

from .utils import barycentric_interpolate, is_point_in_triangle


class Converter:
    """
    Converts vertex-colored .obj meshes to uv-mapped, textured .glb meshes.
    """

    def __init__(self, texture_size: int = 1024, upscale_factor: int = 2,
                 median_filter_size: int = 3, blur_filter_radius: int = 1):
        """
        Initializes the Converter.

        Parameters:
            texture_size (int): The size of the texture to be generated.
            upscale_factor (int): Texture upscaling during mapping. May increase quality at the cost of conversion time.
        """

        self.texture_size = texture_size
        self.upscaling = upscale_factor
        self.buffer_size = texture_size * upscale_factor
        self.median_size = median_filter_size
        self.blur_radius = blur_filter_radius

        self.texture_buffer = np.zeros(
            (self.buffer_size, self.buffer_size, 4), dtype=np.uint8
        )

    def convert(self, input_mesh_path: str, output_mesh_path: str | None = None) -> str:
        """
        Converts the input mesh vertex-colored .obj file to a uv-mapped, textured .glb file.

        Parameters:
            input_mesh_path (str): The path to the input mesh file.
            output_mesh_path (str | None): The path to the output mesh file. If None, the default path is "output.glb".

        Returns:
            str: The path to the output mesh file.
        """

        output_mesh_path = self._validate_output_path(output_mesh_path)

        mesh = trimesh.load(input_mesh_path)
        if not hasattr(mesh, "visual") or not hasattr(mesh.visual, "vertex_colors"):
            warnings.warn("Input mesh must be an obj file with vertex colors.")
            return None

        vertex_colors = mesh.visual.vertex_colors

        vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

        vertices = mesh.vertices[vmapping]
        vertex_colors = vertex_colors[vmapping]

        mesh.vertices = vertices
        mesh.faces = indices

        for face in mesh.faces:
            uv0, uv1, uv2 = uvs[face]
            c0, c1, c2 = vertex_colors[face]

            uv0 = (uv0 * (self.buffer_size - 1)).astype(int)
            uv1 = (uv1 * (self.buffer_size - 1)).astype(int)
            uv2 = (uv2 * (self.buffer_size - 1)).astype(int)

            min_x = max(int(np.floor(min(uv0[0], uv1[0], uv2[0]))), 0)
            max_x = min(int(np.ceil(max(uv0[0], uv1[0], uv2[0]))), self.buffer_size - 1)
            min_y = max(int(np.floor(min(uv0[1], uv1[1], uv2[1]))), 0)
            max_y = min(int(np.ceil(max(uv0[1], uv1[1], uv2[1]))), self.buffer_size - 1)

            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    p = np.array([x + 0.5, y + 0.5])
                    if is_point_in_triangle(p, uv0, uv1, uv2):
                        color = barycentric_interpolate(uv0, uv1, uv2, c0, c1, c2, p)
                        self.texture_buffer[y, x] = np.clip(color, 0, 255).astype(
                            np.uint8
                        )

        self._inpaint_texture()

        self.texture = Image.fromarray(self.texture_buffer)
        self._filter_and_resize_texture()

        material = trimesh.visual.material.PBRMaterial(
            baseColorFactor=[1.0, 1.0, 1.0, 1.0],
            baseColorTexture=self.texture,
            metallicFactor=0.0,
            roughnessFactor=1.0,
        )

        visuals = trimesh.visual.TextureVisuals(uv=uvs, material=material)
        mesh.visual = visuals

        mesh.export(output_mesh_path)

        print(f"Processed mesh saved to {output_mesh_path}")
        return str(output_mesh_path)

    def _validate_output_path(self, output_path: str | None) -> Path:
        """
        Validate and coerce the output path to a .glb file.

        Parameters:
            output_path (str | None): The desired output path.

        Returns:
            Path: A Path object with a .glb extension.
        """
        default_output = Path("output.glb")

        if output_path is None:
            return default_output

        path = Path(output_path)

        if path.suffix.lower() != ".glb":
            new_path = path.with_suffix(".glb")
            warnings.warn(
                f"Output file extension changed from '{path.suffix}' to '.glb'",
                f"Saving as {new_path}",
            )
            return new_path

        return path

    def _inpaint_texture(self) -> None:
        """
        Inpaint the texture buffer to remove holes.
        """
        image_bgra = self.texture_buffer.copy()
        mask = (image_bgra[:, :, 3] == 0).astype(np.uint8) * 255
        image_bgr = cv2.cvtColor(image_bgra, cv2.COLOR_BGRA2BGR)
        inpainted_bgr = cv2.inpaint(
            image_bgr, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA
        )
        inpainted_bgra = cv2.cvtColor(inpainted_bgr, cv2.COLOR_BGR2BGRA)
        self.texture_buffer = inpainted_bgra[::-1]
    
    def _filter_and_resize_texture(self) -> None:
        """
        Filter and resize the texture to reduce artifacts.
        """
        self.texture = self.texture.filter(ImageFilter.MedianFilter(size=self.median_size))
        self.texture = self.texture.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        self.texture = self.texture.resize(
            (self.texture_size, self.texture_size), Image.Resampling.LANCZOS
        )
