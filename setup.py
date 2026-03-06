import setuptools
import os


def get_console_scripts():
    """Generate list of (script_name, module_path) tuples for CLI tools."""
    for filename in os.listdir("./qubesadmin/tools"):
        basename, ext = os.path.splitext(os.path.basename(filename))
        if (
                basename in ["__init__", "dochelpers", "xcffibhelpers"]
                or ext != ".py"
        ):
            continue
        yield basename.replace("_", "-"), f"qubesadmin.tools.{basename}"


if __name__ == "__main__":
    setuptools.setup(
        packages=setuptools.find_packages(),
        entry_points={
            "console_scripts": [f"{name}={module}:main" for name, module in
                                get_console_scripts()]}
    )
