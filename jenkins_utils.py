from __future__ import print_function
import zipfile
from io import BytesIO
import re
import os
import pickle
import time
from shutil import copy

RPK_CPS_MAPPING = {"27" : ("NGM", "ngm"),
                   "13" : ("PTB", "ptb"),
                   "14" : ("CH",  "gch"),
                   "33" : ("NGP", "ngp"),
                   "35" : ("NGP", "ngp")}

def get_suffixes(platform):
    if platform in RPK_CPS_MAPPING:
        return RPK_CPS_MAPPING[platform]
    else:
        return None

def extract_file_from_zip(zip_name, file_name):
    f = None
    z = zipfile.ZipFile(zip_name, 'r')
    if z:
        for i in z.infolist():
            if file_name.lower() == i.filename.lower():
                try:
                    buf = z.read(i.filename)
                except RuntimeError as e:
                    if -1 != str(e).find("password required for extraction"):
                        buf = z.read(i.filename, b"(gogol)")
                    else:
                        raise e
                f = BytesIO(buf)
                short_filename = i.filename
                file_size = len(buf)
                break
    return f

def find_file_in_zip(zip_name, file_pattern):
    z = zipfile.ZipFile(zip_name, 'r')
    if z:
        for i in z.infolist():
            m = re.search(file_pattern, i.filename, re.I)
            if m:
                return i.filename
    return None

def extract_cp_info(z19_name):
    f = extract_file_from_zip(z19_name, "short_info.txt")
    if f:
        txt = f.read().decode()
        m = re.search("CODEPLUG\s\=\s(\d{2})\.?(\d{2})(\-(\d{2}))?", txt, re.M)
        if m:
            if m.group(4):
                return m.group(1)+m.group(2)+"-"+m.group(4)
            else:
                return m.group(1)+m.group(2)
    return None

def get_list_of_cp_zip_names(z19_list, dir):
    ret_list = []
    for r,d,f in os.walk(os.path.abspath(dir)):
        for file in f:
            for z19 in z19_list:
                m = re.search(z19, file, re.I)
                if not m:
                    continue
                m = re.search("[BIRD](\d{2}).*?\.z19$", file, re.I)
                if not m:
                    print("Couldn't extract platform from file name %s" % file)
                    continue
                platform = m.group(1)
                suf = get_suffixes(platform)
                if not suf:
                    print("Unknown platform %s" % platform)
                    continue
                zip_suffix, cps_suffix = suf
                full_path = os.path.realpath(os.path.join(r, file))
                cp = extract_cp_info(full_path)
                if not cp:
                    print("Could not extract CP information for %s" % file)
                    continue
                print("Found %s file and extracted from it CP version %s" % (os.path.join(r, file), cp))
                ret_list.append((cp+"_"+zip_suffix+".zip", zip_suffix, cps_suffix, cp))
    return set(ret_list)

def find_zip_files(z19_list, main_dir, cp_dirs):
    zip_file_list = []
    zips = get_list_of_cp_zip_names(z19_list, main_dir)
    if len(zips) != len(z19_list):
        print(z19_list)
        print(zips)
        raise Exception("Number of z19 files doesn't match number of cp zip files found. "+str(len(zips))+" != "+str(len(z19_list)))

    for z in zips:
        name = z[0]
        params = z[1:]
        print("Searching for %s ..." % name)
        found = False
        dir_list = [main_dir]
        dir_list += cp_dirs
        for dir in dir_list:
            for r,d,f in os.walk(os.path.abspath(dir)):
                for file in f:
                    if file.lower().endswith(name.lower()) or file.lower().endswith(name.lower().replace("-","_")):
                        full_file = os.path.join(r, file)

                        rpk_pattern = ".*"+params[2]+".*\.rpk"
                        f1 = find_file_in_zip(full_file, ".*"+params[2]+".*\.rpk")
                        if not f1:
                            print("Zip file %s found, but doesn't contains *.rpk that match pattern %s." % (full_file, rpk_pattern))
                            continue

                        cps_pattern = ".*"+params[2]+".*\.cps"
                        f2 = find_file_in_zip(full_file, cps_pattern)
                        if not f2:
                            print("Zip file %s found, but doesn't contains *.cps that match pattern %s." % (full_file, cps_pattern))
                            continue

                        rpk_name = params[2]+"_"+params[0]+".rpk"
                        cps_name = "cpu2"+params[2]+params[1]+".cps"

                        print("Zip file %s found with %s and %s required files." % (full_file, f1, f2))
                        zip_file_list.append((os.path.realpath(full_file), time.ctime(os.path.getmtime(full_file)), os.path.getsize(full_file), f1, f2, rpk_name, cps_name))
                        found = True
                        break
            if found:
                break
        if not found:
            raise Exception("Required zip file %s wasn't found." % name)
    return zip_file_list

def find_all_files(file_patterns, home_dir):
    file_list = []
    for p in file_patterns:
        found = False
        for r,d,f in os.walk(os.path.abspath(home_dir)):
            for file in f:
                full_name = os.path.join(r, file)
                m = re.search(p, full_name, re.I)
                if m:
                    if found:
                        raise Exception("More than one file found than match following pattern %s. Make pattern more restrictive.\n\tFirst file %s\n\tSecond file %s" % (p, file_list[-1][0], full_name))
                    file_list.append((os.path.realpath(full_name), time.ctime(os.path.getmtime(full_name)), os.path.getsize(full_name)))
                    print("File %s found that match pattern %s" % (full_name, p))
                    found = True
        if not found:
            raise Exception("Required file than match pattern %s wasn't found." % p)
    return file_list

def find_static_files(static_files):
    file_list = []
    for p in static_files:
        if os.path.isfile(p):
            print("File %s found" % p)
            file_list.append((os.path.realpath(p), time.ctime(os.path.getmtime(p)), os.path.getsize(p)))
        else:
            raise Exception("Required file %s wasn't found." % p)
    return file_list

def get_cur_files_set(z19_files, files, static_files, main_dir, cp_dirs):
    main_dir = os.path.realpath(main_dir)
    zips = find_zip_files(z19_files, main_dir, cp_dirs)
    files = find_all_files(files, main_dir)
    static_files = find_static_files(static_files)
    files += static_files
    return (main_dir, sorted(zips,  key=lambda tup: tup[1]), sorted(files, key=lambda tup: tup[1]))

def dump_files_set(files_set, filename):
    with open(filename, "wb+") as f:
        pickle.dump(files_set, f)

def load_files_set(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return ["", [], []]

def are_files_set_same(set_old, set_new):
    if set_old[0] != set_new[0]:
        desc = "Main directory is different %s != %s" % (set_old[0], set_new[0])
        print(desc)
        return desc

    if len(set_old[1]) != len(set_new[1]):
        desc = "Number of zip files is different %d != %d" % (set_old[1], set_new[1])
        print(desc)
        return desc
    for i in range(len(set_old[1])):
        if len(set_old[1][i]) != len(set_new[1][i]):
            desc = "Number of elem in zip file entry is different %d != %d" % (len(set_old[1][i]), len(set_new[1][i]))
            print(desc)
            return desc
        for x in range(len(set_old[1][i])):
            if set_old[1][i][x] != set_new[1][i][x]:
                desc = "Elem in zip file entry is different %s != %s for %s" % (set_old[1][i][x], set_new[1][i][x], set_old[1][i][0])
                print(desc)
                return desc

    if len(set_old[2]) != len(set_new[2]):
        desc = "Number of monitored files is different %d != %d" % (len(set_old[2]), len(set_new[2]))
        print(desc)
        return desc
    for i in range(len(set_old[2])):
        if len(set_old[2][i]) != len(set_new[2][i]):
            desc = "Number of elem in monitored file entry is different %d != %d" % (len(set_old[2][i]), len(set_new[2][i]))
            print(desc)
            return desc
        for x in range(len(set_old[2][i])):
            if set_old[2][i][x] != set_new[2][i][x]:
                desc = "Elem in monitored file entry is different %s != %s for %s" % (set_old[2][i][x], set_new[2][i][x], set_old[2][i][0])
                print(desc)
                return desc

    return None

def extract_zip_files_and_copy_monitored(files_set, dir):
    for z in files_set[1]:
        f = extract_file_from_zip(z[0], z[3])
        with open(os.path.join(dir, z[5]), "wb+") as f_dst:
            f_dst.write(f.read())
            print("Extracted %s from %s" % (z[5], z[0]))

        f = extract_file_from_zip(z[0], z[4])
        with open(os.path.join(dir, z[6]), "wb+") as f_dst:
            f_dst.write(f.read())
            print("Extracted %s from %s" % (z[6], z[0]))

    for f in files_set[2]:
        copy(f[0], dir)
        print("Copied %s" % f[0])

def dump_history_file(history, filename):
    with open(filename, "wb+") as f:
        pickle.dump(history, f)

def load_history_file(filename):
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)
    return []

def update_history(build_number, build_directory, history_file, dest_dir):
    m = re.search("(\d{4}.?)$", build_directory)
    if m:
        history = load_history_file(history_file)
        history.append((m.group(1), build_number, time.time()))
        dump_history_file(history, history_file)
        print("HISTORY: Added %s : #%s - %s entry to %s file." % (history[-1][0], history[-1][1], history[-1][2], history_file))
    else:
        print("HISTORY: Failed to find pattern that match build number in %s." % (build_directory))
    copy(history_file, dest_dir)

def get_build_number_from_history(build_ver, history_file):
    history = load_history_file(history_file)
    last_time = 0.0
    last_ver = None
    for h in history:
        if h[0] == build_ver:
            if last_time < h[2]:
                last_time = h[2]
                last_ver = h[1]
    return last_ver


def get_latest_directories(directory):
    dirs = []
    for d in os.listdir(directory):
        full_path = os.path.join(directory, d)
        if os.path.isdir(full_path):
            try:
                os.listdir(full_path)
                dirs.append(full_path)
            except WindowsError:
                pass

    if len(dirs) > 0:
        return max(dirs, key=os.path.getmtime)
    else:
        return None
