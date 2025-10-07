# Contributing to JSBSim2Blender

Thank you for considering contributing to **JSBSim2Blender**! We welcome contributions that enhance the functionality, usability, and documentation of this project.

## How You Can Help

There are several ways you can contribute:

- **Bug Reports**: If you encounter issues or unexpected behavior, please report them.
- **Feature Requests**: Suggest new features or improvements.
- **Code Contributions**: Submit pull requests with bug fixes, enhancements, or new features.
- **Documentation**: Help improve this README, add examples, or clarify existing content.

---

## Code Style Guidelines

To maintain consistency across the project, please adhere to the following coding standards:

- **PEP 8 Compliance**: Follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code.
- **Line Length**: Limit all lines to a maximum of 88 characters.
- **Linter**: Use [flake8](https://flake8.pycqa.org/en/latest/) and [pylint](https://github.com/pylint-dev/pylint) to check your code.

### Options for running Flake8 and Pylint

**1. Command-line installation (cross-platform):**

   ```bash
   pip install flake8 pylint
   flake8 . --config setup.cfg
   pylint --rcfile setup.cfg .
   ```

**2. Using VS Code (simplest for most contributors):**

1. Install the [**Python extension**](https://marketplace.visualstudio.com/items?itemName=ms-python.python) by Microsoft in VS Code.
2. Install the [**Flake8 VS Code extension**](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8) (search for "Flake8" in the Extensions Marketplace).  
3. Install the [**Pylint VS Code extension**](https://marketplace.visualstudio.com/items?itemName=ms-python.pylint) (search for "Pylint" in the Extensions Marketplace).  
4. Make sure your project virtual environment is selected as the Python interpreter in VS Code.  
5. Flake8 and Pylint will automatically highlight PEP 8 violations in the editor as you save files.  

---

## Pull Request Process

When submitting a pull request (PR):

1. **Fork the Repository**: Create a fork of this repository.
2. (Optional but recommended) Install `fake-bpy-module-latest` in your python virtual environment to get **code completion and highlighting** for Blender's Python API:

   ```bash
   pip install fake-bpy-module-latest
   ```
3. **Create a Branch**: Make your changes in a new branch, not directly in `main`.
4. **Commit Changes**: Write clear and concise commit messages.
5. **Push Changes**: Push your changes to your forked repository.
6. **Open a Pull Request**: Submit a PR from your branch to our `main` branch.

Please ensure your PR:

- Addresses a single concern or feature.
- Includes tests where applicable.
- Updates documentation if necessary.

---

## Building the Extension

If you are making code changes and want to test or package the extension:

1. **Install Blender** and make sure it is available in your system `PATH`.
2. Open the project in **VS Code**.
3. Use the included VSCode **Build Addon** task:
   - Press `Ctrl+Shift+B` (Windows/Linux) or `Cmd+Shift+B` (Mac) to run the default build task.
   - This will call Blender to package the extension automatically.
4. The packaged extension `.zip` file will be generated in the **current project directory**.
5. You can then install this `.zip` extension in Blender to test your changes.

---

## Reporting Issues

If you find a bug or have a question:

- **Search Existing Issues**: Before creating a new issue, check if it has already been reported.
- **Provide Details**: Include steps to reproduce the issue, your environment details (e.g., Blender version, operating system), and any relevant logs or screenshots.
