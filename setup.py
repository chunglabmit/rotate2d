import setuptools

setuptools.setup(
    name="rotate2d",
    author="Kwanghun Chung Lab",
    description="UI for rigid rotation of ZARR file",
    packages=["rotate2d"],
    install_requires=[
        "matplotlib",
        "numpy",
        "scipy",
        "zarr",
        "PyQt5"
    ],
    entry_points=dict(console_scripts=["rotate2d=rotate2d.r2dapp:run_application"]),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.5"
    ]
)