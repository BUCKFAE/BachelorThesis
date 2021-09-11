import subprocess
import time
print("Running test communication program!")

command_build = "docker-compose build".split(" ")
command_shell = "docker-compose run --entrypoint pokemon-showdown/pokemon-showdown --rm showdown".split(" ")


print(f"Executing command: \"{command_build}\"")

res = subprocess.Popen(command_build, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

print("Building container...")
while "DONE" not in res.stdout.readline().decode(): pass
print("Done!")

print(f"Executing command: \"{command_shell}\"")
res2 = subprocess.Popen(command_shell, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

print("Sleeping")
time.sleep(5)
print("Done")






print("Done, now in container")

res2.stdin.write("echo hi".encode())
print("written")
res2.stdin.flush()
print("Flushed")
print(res2.stdout.readlines().decode())
#res.stdin.flush()

print("Done")

#print(res.stdout.readline().decode())
#print(res.stdout.readline().decode())


#res.stdin.write("6\n".encode())
#res.stdin.flush()

#print(res.stdout.readline().decode())