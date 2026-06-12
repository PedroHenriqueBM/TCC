import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import os
from pathlib import Path

from Model.SystemTest.IntelligentSystemTestAgent.Policy import SystemTestPolicy
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class TestExecutionResult:

    def __init__(self, passed: bool, stdout: str, stderr: str,
                 rewritten: bool = False, video_path: str | None = None):
        self.passed = passed
        self.stdout = stdout
        self.stderr = stderr
        self.rewritten = rewritten
        self.video_path = video_path


class IntelligentSystemTestAgent:

    def __init__(self):
        self.__policy = SystemTestPolicy()
        self.__client = get_openai_client()

    def consults_policy(self) -> SystemTestPolicy:
        return self.__policy

    def execute_script(self, script_path: str, timeout: int = 120,
                       video_output_dir: str | None = None) -> tuple[bool, str, str, str | None]:
        """
        Runs the test script via subprocess.

        If video_output_dir is provided, injects record_video_dir into the script
        so Playwright records the execution as WebM. Returns the video path once found.

        Returns (passed, stdout, stderr, video_path).
        """
        content = self.__read_and_prepare_headless(script_path)

        if video_output_dir:
            content = self.__inject_video_recording(content, video_output_dir)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        video_path: str | None = None
        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            passed = result.returncode == 0
            stdout, stderr = result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            passed = False
            stdout = ""
            stderr = f"Script excedeu o tempo limite de {timeout} segundos."
        except Exception as e:
            passed = False
            stdout = ""
            stderr = str(e)
        finally:
            os.unlink(tmp_path)

        if video_output_dir:
            time.sleep(3)  # wait for Playwright to flush WebM
            webm_files = list(Path(video_output_dir).glob("*.webm"))
            if webm_files:
                video_path = str(sorted(webm_files)[-1])

        return passed, stdout, stderr, video_path

    def rewrite_script(self, script_path: str, error: str, acceptance_criteria: str) -> str:
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        prompt = self.__policy.get_rewrite_prompt(
            script=script_content,
            error=error,
            acceptance_criteria=acceptance_criteria,
        )

        response = self.__client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.__policy.get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )

        new_script = response.choices[0].message.content
        new_script = self.__extract_code(new_script)
        new_script = self.__read_and_prepare_headless_from_content(new_script)

        rewritten_path = script_path.replace(".py", "_rewritten.py")
        with open(rewritten_path, "w", encoding="utf-8") as f:
            f.write(new_script)

        return rewritten_path

    def evaluate_with_pdf(self, pdf_path: str, requirement_name: str,
                          acceptance_criteria: str, script_content: str = "",
                          previous_comments: str = "") -> tuple[str, bool]:
        """
        Evaluates test pass/fail by sending the recording PDF to GPT (multimodal).
        This is the primary evaluation method — the script is only context.
        Returns (evaluation_text, passed).
        """
        prompt = self.__policy.get_pdf_evaluation_prompt(
            requirement_name=requirement_name,
            acceptance_criteria=acceptance_criteria,
            script_summary=script_content,
            previous_comments=previous_comments,
        )

        uploaded_id = None
        try:
            with open(pdf_path, "rb") as f:
                uploaded = self.__client.files.create(
                    file=(Path(pdf_path).name, f, "application/pdf"),
                    purpose="assistants",
                )
            uploaded_id = uploaded.id

            response = self.__client.responses.create(
                model="gpt-4o",
                input=[
                    {"role": "system", "content": self.__policy.get_system_prompt()},
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_file", "file_id": uploaded_id},
                        ],
                    },
                ],
            )

            raw = response.output_text
            try:
                data = json.loads(raw)
                return data.get("evaluation", raw), bool(data.get("passed", False))
            except json.JSONDecodeError:
                # Try to extract JSON from text
                match = re.search(r'\{.*"passed".*\}', raw, re.DOTALL)
                if match:
                    data = json.loads(match.group(0))
                    return data.get("evaluation", raw), bool(data.get("passed", False))
                return raw, False

        finally:
            if uploaded_id:
                try:
                    self.__client.files.delete(uploaded_id)
                except Exception:
                    pass

    def generate_evaluation_comment(self, requirement_name: str, acceptance_criteria: str,
                                     returncode_passed: bool, stdout: str, stderr: str,
                                     previous_comments: str = "") -> tuple[str, bool]:
        """
        Returns (evaluation_text, ai_determined_passed).

        The AI re-evaluates whether the acceptance criteria were actually verified,
        not just whether the script exited cleanly.
        """
        prompt = self.__policy.get_evaluation_prompt(
            requirement_name=requirement_name,
            acceptance_criteria=acceptance_criteria,
            returncode_passed=returncode_passed,
            stdout=stdout,
            stderr=stderr,
            previous_comments=previous_comments,
        )

        response = self.__client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.__policy.get_system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )

        try:
            data = json.loads(response.choices[0].message.content)
            return data.get("evaluation", ""), bool(data.get("passed", False))
        except (json.JSONDecodeError, AttributeError):
            raw = response.choices[0].message.content
            return raw, returncode_passed

    def run_test_with_retry(self, script_path: str, acceptance_criteria: str,
                             timeout: int = 120,
                             video_output_dir: str | None = None) -> TestExecutionResult:
        """
        Runs the test. If it fails due to an interface change, rewrites and retries.
        Video is recorded only on the first attempt.
        """
        passed, stdout, stderr, video_path = self.execute_script(
            script_path, timeout, video_output_dir=video_output_dir
        )

        if not passed and self.__is_interface_change_error(stderr):
            print("  -> Interface mudou. Reescrevendo script com auxílio da IA...")
            rewritten_path = self.rewrite_script(script_path, stderr, acceptance_criteria)
            # Retry without video (already captured or failed)
            passed, stdout, stderr, _ = self.execute_script(rewritten_path, timeout)
            return TestExecutionResult(passed=passed, stdout=stdout, stderr=stderr,
                                       rewritten=True, video_path=video_path)

        return TestExecutionResult(passed=passed, stdout=stdout, stderr=stderr,
                                   rewritten=False, video_path=video_path)

    # ── Private helpers ───────────────────────────────────────────────────────

    def __is_interface_change_error(self, stderr: str) -> bool:
        patterns = [
            "TimeoutError", "ElementHandle", "selector", "locator",
            "waiting for", "not found", "not visible", "not attached",
        ]
        return any(p.lower() in stderr.lower() for p in patterns)

    def __read_and_prepare_headless(self, script_path: str) -> str:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.__read_and_prepare_headless_from_content(content)

    def __read_and_prepare_headless_from_content(self, content: str) -> str:
        content = re.sub(r"headless\s*=\s*False", "headless=True", content)
        if "headless" not in content:
            content = content.replace(
                "p.chromium.launch_persistent_context(",
                "p.chromium.launch_persistent_context(\n            headless=True,",
            )
            content = content.replace(
                "p.chromium.launch(",
                "p.chromium.launch(headless=True,",
            )
        return content

    def __inject_video_recording(self, content: str, video_dir: str) -> str:
        """Add record_video_dir to browser.new_context() in the script."""
        vd = video_dir.replace("\\", "/")
        size = '{"width": 1280, "height": 720}'

        # Pattern 1: empty new_context()
        content = re.sub(
            r"await\s+browser\.new_context\(\s*\)",
            f'await browser.new_context(record_video_dir=r"{vd}", record_video_size={size})',
            content,
        )
        # Pattern 2: non-empty new_context( — inject at start (negative lookahead)
        content = re.sub(
            r"await\s+browser\.new_context\((?!record_video_dir)",
            f'await browser.new_context(record_video_dir=r"{vd}", record_video_size={size}, ',
            content,
        )
        # Pattern 3: launch_persistent_context without new_context (original manual scripts)
        if "record_video_dir" not in content:
            content = re.sub(
                r"(launch_persistent_context\([^)]*headless=True)",
                r'\1, record_video_dir=r"' + vd + r'", record_video_size=' + size,
                content,
            )
        return content

    def __extract_code(self, text: str) -> str:
        match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r"```\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
