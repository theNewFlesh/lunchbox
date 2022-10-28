import subprocess as proc

versions = [7, 8, 9, 10]
versions = [f'python3.{v}' for v in versions]
for v in versions:
    cmd = f'{v} -c "import wrapt"'
    result = proc.Popen(cmd, shell=True, stderr=proc.PIPE)
    result.wait()

    red = '\033[0;91m'
    green = '\033[0;92m'
    clear = '\033[0m'
    state = f'{green}pass{clear}'
    if result.stderr.read() != b'':
        state = f'{red}fail{clear}'
    print(f'{v:<11} {state}')
