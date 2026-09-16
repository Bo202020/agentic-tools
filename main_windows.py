import subprocess
import threading
import uuid

class PowerShellTool:
    def __init__(self):
        self.process = subprocess.Popen(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NoExit",
                "-Command",
                "-"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self.lock = threading.Lock()

    def run(self, command: str):
        with self.lock:
            marker = f"__VECTOR_DONE_{uuid.uuid4().hex}"

            wrapped = f"""

            {command}
            status = $?
            Write-Output "{marker}:$status"
            """

            self.process.stdin.write(wrapped + "\n")
            self.process.stdin.flush()

            output = []

            while True:
                line = self.process.stdout.readline()

                if line == "" and self.process.poll() is not None:
                    raise RuntimeError("Powershell proccess died")

                line = line.rstrip("\r\n")

                if line.startswith(marker):
                    success = line.split(":", 1)[1].lower() == "true"
                    break

                output.append(line)

            return {
                "success": success,
                "output": "\n".join(output)
            }

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.write("exit\n")
            self.process.stdin.flush()



shell = PowerShellTool()

print(shell.run("Get-Location"))
print(shell.run("cd C:\\Users\\Daniel\\Documents"))
print(shell.run("Get-Location"))
shell.run('$name = "Bogdan"')
print(shell.run("echo $name"))
