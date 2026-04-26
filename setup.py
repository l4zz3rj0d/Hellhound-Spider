from setuptools import setup

setup(
    name="hellhound-spider",
    version="12.3",
    description="Fast async web crawler for security testing",
    author="Sree Danush S",
    author_email="lazzer@gmail.com",
    url="https://github.com/project-hellhound-org/hellhound-spider",
    py_modules=["spider"],
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
    ],
    extras_require={
        "spa": ["playwright>=1.40.0"],
    },
    entry_points={
        "console_scripts": [
            "spider=spider:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Operating System :: OS Independent",
    ],
)

## Author

<table>
  <tr>
    <td align="center">
      <a href="https://l4zz3rj0d.github.io">
        <img src="https://github.com/l4zz3rj0d.png" width="100px;" alt="L4ZZ3RJ0D" style="border-radius:50%;"/><br />
        <sub><b>L4ZZ3RJ0D</b></sub>
      </a>
    </td>
    <td>
      <b>Sree Danush S</b><br />
      Cybersecurity student · Offensive security builder · CyArt intern<br /><br />
      <a href="https://l4zz3rj0d.github.io"><img src="https://img.shields.io/badge/GitHub-l4zz3rj0d-c0392b?style=flat-square&logo=github" alt="GitHub"/></a>
      <a href="https://tryhackme.com/p/l4zz3rj0d"><img src="https://img.shields.io/badge/TryHackMe-Top%201%25-e8a020?style=flat-square" alt="TryHackMe"/></a>
      <a href="https://medium.com/@l4zz3rj0d"><img src="https://img.shields.io/badge/Medium-@l4zz3rj0d-c8945a?style=flat-square&logo=medium" alt="Medium"/></a>
    </td>
  </tr>
</table>