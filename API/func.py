from subprocess import DEVNULL, PIPE, Popen
def convert_seconds_to_hhmm(seconds):
    hours, minutes = divmod(seconds, 3600)
    return f"{hours:02}:{minutes // 60:02}"

def truncate_string(s, max_length):
    return s if len(s) <= max_length else f"{s[:max_length - 3]}..."

def run_command(command):
    process = Popen(command, stdout=PIPE, universal_newlines=True, shell=True, stderr=DEVNULL)
    return process.communicate()[0].strip()
