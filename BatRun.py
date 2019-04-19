import os
from subprocess import Popen, PIPE, STDOUT
import time
import argparse
from os.path import exists, join
import threading
import shutil


def iter_files(path):
    """Walk through all files located under a root path."""
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for dir_path, _, file_names in os.walk(path):
            for f in file_names:
                yield os.path.join(dir_path, f)
    else:
        raise RuntimeError('Path %s is invalid' % path)


def pdf2html(cmd):
    Popen(cmd, shell=True)


def movefile(file,dir_name, old_path):
    try:
        shutil.copy(file, old_path)
        os.remove(file)
        shutil.rmtree(dir_name)
    except:
        pass


def kill_tasks():
    task_list = ["pdf2html.exe", "Acrobat.exe", "AcroCEF.exe"]
    for task in task_list:
        cmd = "tasklist | findstr \"%s\"" % task
        kill = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        info = kill.stdout.readlines()
        for each in info:
            each = each.decode('utf-8')
            Popen("taskkill /pid %s -t -f" % each.split()[1], stdout=PIPE, stderr=STDOUT, shell=True)


def main(args):
    if not exists(args.input):
        raise FileNotFoundError
        exit()
    if not exists(args.output):
        os.makedirs(args.output)
    old_path = args.oldpath
    if not exists(old_path):
        os.makedirs(old_path)
    HAVE_DONE = len(os.listdir(args.output))
    print("Files have been converted will be move to:\n%s" % old_path)
    print("Having converted %d" % HAVE_DONE)
    print("############ Starting Converting ############")

    files = list(iter_files(args.input))
    for id, file in enumerate(files):
        
        name, _ = os.path.splitext(os.path.basename(file))
        dir_name = join(args.output, name)
        save_path = join(args.output, name + '.' + args.format)
        if os.path.exists(save_path):
            print('%d/%d done!' % (id, len(files)))
            movefile(file,dir_name,old_path)
            continue
            
        cmd = "%s -i %s -o %s -f %s" % (args.exe, file, args.output, args.format)
        thread = threading.Thread(target=pdf2html, args=(cmd,))
        thread.start()
       
        start_time = time.time()
        while True:
            if os.path.exists(save_path):
                print('%d/%d done!' % (id, len(files)))
                break
            if time.time() - start_time > args.timeout:
                print('%d/%d fail!' % (id, len(files)))
                kill_tasks()
                break
        # print(time.time() - start_time)
        movefile(file,dir_name,old_path)

        if id%20==0:
            kill_tasks()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='bat run of the pdf2html')

    parser.add_argument('--input', '-i', required=True, action='store',
                        help='Path of files you want to convert')
    parser.add_argument('--output', '-o', default=join(os.getcwd(), 'output'), action='store',
                        help='Path to store converted files')
    parser.add_argument('--oldpath', required=True ,help='Path to store old pdfs')
    parser.add_argument('--exe', '-e', required=True, action='store',
                        help='Path of pdf2html.exe')
    parser.add_argument('--replace', '-r', default=False, action='store',
                        help='Whether replace exist files')
    parser.add_argument('--timeout', '-t', type=float, default=20, action='store',
                        help='Timeout for a single convert')
    parser.add_argument('--format', '-f', default='html', action='store',
                        help='Format you want to convert: '
                             'xml, txt, doc, docx, '
                             'ps, jpeg, jpe, jpg, jpf, '
                             'jpx, j2k, j2c, jpc, rtf, '
                             'accesstext, tif, tiff')
    args = parser.parse_args()
    main(args)
