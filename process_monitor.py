import win32con
import win32api
import win32security
 
import wmi
import sys
import os
 
# 保存数据到文件中
def log_to_file(message):
    fd = open("process_monitor_log.csv", "ab")
    fd.write("%s\r\n" % message)
    fd.close()
 
    return
 
# 创建一个日志文件的头
log_to_file("Time,User,Executable,CommandLine,PID,Parent PID,Privileges")
 
# 初始化WMI接口
c = wmi.WMI()
 
# 创建进程监控器（监控进程创建）
process_watcher = c.Win32_Process.watch_for("creation")
 
while True:
    try:
        # 有创建进程事件会返回
        new_process = process_watcher()
 
        proc_owner = new_process.GetOwner()
        # for i in proc_owner:
        #     print i
        proc_owner = "%s\\%s" % (proc_owner[0], proc_owner[2])
        # 时间
        create_data = new_process.CreationDate
        # 路径
        executable = new_process.ExecutablePath
        # 命令行（就是实际的命令是什么）
        cmdline = new_process.CommandLine
        pid = new_process.ProcessId
        parent_pid = new_process.ParentProcessId
 
        # N/A：不可用的意思
        privileges = "N/A"
 
        process_log_message = "%s,%s,%s,%s,%s,%s,%s\r\n" % (create_data, proc_owner, executable, cmdline, pid, parent_pid, privileges)
 
        # print process_log_message
 
        log_to_file(process_log_message)
 
    except:
        pass
