import venv
import subprocess
import tempfile
from pathlib import Path

from cat.experimental.form import form, CatForm, CatFormState
from .code_model import CodeModel
from .settigns import Settings

@form
class CodeForm(CatForm):
    model_class = CodeModel
    ask_confirm = True

    name = "Python Code Runner"
    description = "Use this action to write and execute Python code."
    start_examples = [
        "Write a simple python code",
        "White a python code that uses numpy",
        "Execute this code",
        "Run a python code that uses pandas",
        "Run it",
        "What is the output of this code?",
        "What will this code do?",
    ]

    # SECTION: Form methods

    def update(self):
        super().update()
        settings = Settings(**self.cat.mad_hatter.get_plugin().load_settings())
        if settings.quick_execute and self._state == CatFormState.COMPLETE:
            # If the form is complete, check if the user asked to execute the code
            execution_confirmed = self._model.get("execution_confirmed", False) 
            self.ask_confirm = not execution_confirmed

    def submit(self, form_data):
        code = CodeModel(**form_data)

        if not code.code:
            return {
                "output": "The code is empty. Please write a valid python code."
            }

        if code.code_lang.lower() != "python":
            return {
                "output": "Only Python code is supported. Please write a valid python code."
            }

        return {
            "output": self._execute(code)
        }
     
    def message_wait_confirm(self):
        code_model = CodeModel(**self._model)

        if code_model.explain_to_user is not None:
            self.cat.send_chat_message(code_model.explain_to_user)

        # Set the code block if not present
        confirm_message = code_model.code
        if not confirm_message.startswith("```"):
            message = f"```python\n{confirm_message}\n"
        if not confirm_message.endswith("```"):
            confirm_message = f"{message}\n```"


        if code_model.dependencies:
            confirm_message += f"\nDependencies: {', '.join(code_model.dependencies)}\n"

        settings = Settings(**self.cat.mad_hatter.get_plugin().load_settings())
        if settings.show_warnings:
            confirm_message += "\n\n**WARNING**: This code will be executed in your system.\n**Make sure the code is safe to execute**"

        confirm_message += "\nDo you want to execute this code?"

        return {
            "output": confirm_message,
        }
            
    def message_closed(self):
        return {
            "output": "Code execution is cancelled."
        }

    # SECTION: Script execution methods

    def _execute(self, code_model: CodeModel) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:

            self.cat.send_notification("Creating virtual environment")
            venv_path = Path(temp_dir) / "venv"
            venv.create(venv_path, with_pip=True)

            if code_model.dependencies:
                self.cat.send_notification("Installing dependencies")
                if error := self._install_dependencies(venv_path, code_model.dependencies) is not None:
                    return f"Error installing dependencies:\n```\n{error}\n```"
            
            code_file = Path(temp_dir) / "code.py"
            python_path = venv_path / "bin" / "python"

            self._save_code_to_file(code_file, code_model.code)
            self.cat.send_notification("Executing code")

            return self._run_script(python_path, code_file)
                       
    def _run_script(self, python_path: Path, code_path: Path) -> str:
        try:
            result = subprocess.run(
                [str(python_path), str(code_path)],
                check=True,
                capture_output=True,
                text=True
            )
            output = f"Output:\n```\n{result.stdout}\n```"
            return output
        except subprocess.CalledProcessError as e:
            return f"Execution error:\n```\n{e.stderr}\n```"
        except Exception as e:
            return f"Error executing code:\n```\n{e}\n```"
        
    def _install_dependencies(self, venv_path: Path, dependencies: list[str] = []) -> str | None:
        pip_path = venv_path / "bin" / "pip"
        try:
            subprocess.run(
                [str(pip_path), "install", *dependencies],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return f"Error installing dependencies:\n```\n{e.stderr}```"

    def _save_code_to_file(self, path: Path, content: str) -> None:
        # Find code block
        start = content.find("```python")
        end = content.find("```", start+1)

        # If code block is found extract the code
        if start != -1 and end != -1:
           code_block = content[start:end]
           code = code_block.replace("```python", "").strip()
        else:
            code = content

        path.write_text(code, encoding="utf-8")

