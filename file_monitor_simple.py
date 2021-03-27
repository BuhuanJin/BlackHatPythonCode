import tempfile
import threading
import win32file
import win32con
import os

# 这些是典型的临时文件所在路径,就是我们监控的目录
dirs_to_monitor = ["C:\\WINDOWS\\Temp",tempfile.gettempdir()]

# 文件修改行为对应常量
FILE_CREATE = 1
FILE_DELETE = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5


# 为每个监控器起一个线程（用Thread来调用这监控器函数）
def start_monitor(path_to_watch):

    # 访问模式
    FILE_LIST_DIRECTORY = 0x0001

    # 获取文件目录句柄
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ |win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    while 1:
        try:
            # 这函数会在目录结构改变时通知我们
            results = win32file.ReadDirectoryChangesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None
            )

            # 获得发生了何种改变，以及目标文件的名称
            for action,file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)

                if action == FILE_CREATE:
                    print "[ + ] Created %s" % full_filename
                elif action == FILE_DELETE:
                    print "[ - ] Deleted %s" % full_filename
                elif action == FILE_MODIFIED:
                    print "[ * ] Modified %s" % full_filename
                    # 输出文件内容
                    print "[vvv] Dumping contents..."
                    try:
                        # 打开文件读数据
                        fd = open(full_filename, "rb")
                        contents = fd.read()
                        fd.close()
                        print contents
                        print "[^^^] Dump complete."
                    except:
                        print "[!!!] Failed."

                    # 文件和文件扩展名分离
                    filename, extension = os.path.splitext(full_filename)
                    if extension in file_types:
                        inject_code(full_filename, extension, contents)

                # 重命名哪个文件
                elif action == FILE_RENAMED_FROM:
                    print "[ > ] Renamed from: %s" % full_filename
                # 重命名后的文件名
                elif action == FILE_RENAMED_TO:
                    print "[ < ] Renamed to: %s" % full_filename
                else:
                    print "[???] Unknown: %s" % full_filename
        except:
            pass


for path in dirs_to_monitor:
    monitor_thread = threading.Thread(target=start_monitor,args=(path,))
    print "Spawning monitoring thread for path: %s" % path
    monitor_thread.start()
