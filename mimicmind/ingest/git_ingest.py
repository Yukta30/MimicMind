import subprocess, json
from pathlib import Path

def run(cmd: list[str], cwd: str | None = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd).decode("utf-8", errors="ignore")

class GitIngest:
    def __init__(self, repo_path: str):
        self.repo = Path(repo_path)

    def iter_commits(self, max_count: int | None = 50):
        fmt = "%H%x01%an%x01%ae%x01%ad%x01%s%x01%b"
        log_cmd = ["git","log","--date=iso","--pretty=format:"+fmt]
        if max_count: log_cmd += [f"-n{max_count}"]
        for line in run(log_cmd, cwd=str(self.repo)).splitlines():
            h,a,e,d,s,b = line.split("\x01")
            diff = run(["git","show","--format=","-U3",h], cwd=str(self.repo))
            yield {"hash":h,"author":a,"email":e,"date":d,"subject":s,"body":b,"diff":diff}

    def export_jsonl(self, out_path: str, max_count: int | None = 200):
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path,"w",encoding="utf-8") as f:
            for c in self.iter_commits(max_count=max_count):
                f.write(json.dumps(c, ensure_ascii=False)+"\n")
