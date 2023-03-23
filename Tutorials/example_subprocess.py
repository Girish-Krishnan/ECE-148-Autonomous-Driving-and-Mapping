import subprocess

# replace "script.sh" with the name of your bash script
script_path = "trial.sh"

# run the script and capture the output
output = subprocess.check_output(["bash", script_path])

# print the output
print(output.decode())
