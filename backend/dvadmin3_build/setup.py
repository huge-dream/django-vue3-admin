import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dvadmin3-build",
    version="1.0.0",
    author="DVAdmin",
    author_email="liqiang@django-vue-admin.com",
    description="一款适用于django-vue3-admin 编译打包exe、macOS的dmg文件等打包工具。支持加密代码、一键启动项目，无需考虑环境。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/huge-dream/dvadmin-build",
    packages=setuptools.find_packages(),
    python_requires='>=3.7, <4',
    install_requires=[
        "pyinstaller>=6.8.0",
        "PyQt6>=6.4.2",
        "psutil==6.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)
