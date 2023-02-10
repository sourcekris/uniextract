
import os.path

def prepare_exe(exe, tool_path, file=None, ext=None):
    exe = exe.replace("$tools", tool_path)

    if file:
        exe = exe.replace("$file", file)
    
    if ext:
        exe = exe.replace("$e", ext)
    
    return exe

def prepare_cmdline(exe, cmdline, tool_path, destdir=None, archive=None, file=None, ext=None):
    cmdline = cmdline.replace("$tools", tool_path)
    cmdline = cmdline.replace("$tool", exe)
    winarc = "z:" + archive.replace("/","\\\\")

    if archive:
        basename = os.path.splitext(os.path.basename(archive))[0]
        cmdline = cmdline.replace("$basename", basename)
        cmdline = cmdline.replace("$archive", archive)
        cmdline = cmdline.replace("$winarchive", winarc)
        cmdline = cmdline.replace("$arcloc", os.path.dirname(archive))
    
    if destdir:
        windest = "z:" + destdir.replace("/","\\\\")
        cmdline = cmdline.replace("$windestdir", windest)
        cmdline = cmdline.replace("$winarchive", winarc)
        cmdline = cmdline.replace("$destdir", destdir)
    
    if ext and archive:
        if len(basename) > 8: 
            cmdline = cmdline.replace("$shortname", basename[:6]+"~1"+ext) # for dos unpackers, but ~1 might not be good enough?
        else:
            cmdline = cmdline.replace("$shortname", basename+ext)
    
    if file:
        cmdline = cmdline.replace("$file", file)
    
    return cmdline
    