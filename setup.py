from setuptools import setup, Extension
from wheel.bdist_wheel import bdist_wheel


class bdist_wheel_abi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            # on CPython, our wheels are abi3 and compatible back to 3.10
            return "cp310", "abi3", plat

        return python, abi, plat


setup(
    cmake_source_dir="./src",
    cmdclass={"bdist_wheel": bdist_wheel_abi3},
)
