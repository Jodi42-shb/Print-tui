import re
import subprocess


def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def get_printers():
    """Returns a list of structured printer objects by parsing lpstat -p"""
    success, stdout = run_cmd(["lpstat", "-p"])
    if not success:
        return []

    printers = []
    for line in stdout.split("\n"):
        if line.startswith("printer "):
            parts = line.split(" ")
            if len(parts) >= 4:
                name = parts[1]
                # 'printer HP is idle. enabled since...' -> state = 'idle'
                status_part = " ".join(parts[2:]).split(".")[0]
                state = status_part.replace("is ", "").strip()
                printers.append({"name": name, "state": state, "raw": line})
    return printers


def get_default_printer():
    """Returns the name of the system default printer"""
    success, stdout = run_cmd(["lpstat", "-d"])
    if success and stdout.startswith("system default destination: "):
        return stdout.replace("system default destination: ", "").strip()
    return None


def get_jobs():
    """Returns a list of active print jobs"""
    success, stdout = run_cmd(["lpstat", "-o"])
    jobs = []
    if success and stdout:
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            parts = re.split(r"\s+", line.strip())
            if len(parts) >= 4:
                job_id = parts[0]
                user = parts[1]
                size = parts[2]
                time = " ".join(parts[3:])
                jobs.append({"id": job_id, "user": user, "size": size, "time": time})
    return jobs


def get_printer_options(printer_name):
    """Returns a dictionary of raw lpoptions for a given printer"""
    success, stdout = run_cmd(["lpoptions", "-p", printer_name, "-l"])
    options = {}
    if success and stdout:
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            parts = line.split(":")
            if len(parts) >= 2:
                key = parts[0].strip()
                values = parts[1].strip()
                options[key] = values
    return options


def print_file(printer_name, file_path, copies=1, sides=None, media=None):
    """Executes the lp command to print a file"""
    cmd = ["lp", "-d", printer_name, "-n", str(copies)]
    if sides and sides != "default":
        cmd.extend(["-o", f"sides={sides}"])
    if media and media != "default":
        cmd.extend(["-o", f"media={media}"])
    cmd.append(file_path)
    return run_cmd(cmd)


def cancel_job(job_id):
    """Cancels a specific print job"""
    return run_cmd(["cancel", job_id])


def enable_printer(printer_name):
    """Enables a printer"""
    return run_cmd(["cupsenable", printer_name])


def disable_printer(printer_name, reason="Disabled via PrintTUI"):
    """Disables a printer"""
    return run_cmd(["cupsdisable", "-r", reason, printer_name])


def delete_printer(printer_name):
    """Deletes a printer queue (requires admin privileges, may prompt if Polkit intercepts)"""
    return run_cmd(["lpadmin", "-x", printer_name])


def set_default_printer(printer_name):
    """Sets the system default printer"""
    return run_cmd(["lpadmin", "-d", printer_name])
