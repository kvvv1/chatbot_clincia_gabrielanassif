from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chatbot-clinica",
    version="1.0.0",
    author="Clínica Gabriela Nassif",
    author_email="suporte@clinica.com",
    description="Assistente virtual no WhatsApp para agendamento de consultas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/chatbot-clinica",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chatbot-clinica=run:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 