import subprocess, time


start = time.time()
r = subprocess.Popen('7za e -bd -so Rocket-0-999.xml.7z 2>/dev/null', shell=True, stdout=subprocess.PIPE, bufsize=65535).stdout
for i in xrange(100000):
    r.read(1024)

print "time with subprocess.Popen : ", time.time() - start
r.close()

