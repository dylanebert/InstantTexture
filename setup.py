from setuptools import setup, find_packages

setup(
    name="instant_texture",
    version="0.1.0",
    description="Convert vertex-colored .obj meshes to uv-mapped, textured .glb meshes.",
    author="Dylan Ebert",
    author_email="dylan.ebert@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "trimesh",
        "xatlas",
        "opencv-python",
        "Pillow",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    license="MIT",
    keywords="mesh, texture, uv, mapping, obj, glb",
    python_requires=">=3.7",
)
