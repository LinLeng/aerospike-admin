# Copyright 2013-2020 Aerospike, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from builtins import str
from builtins import object
from distutils.version import LooseVersion

import ntpath
import os
import shutil
import tarfile
import zipfile


from lib.collectinfo.reader import CollectinfoReader
from lib.collectinfo.cinfolog import CollectinfoLog
from lib.utils.constants import ADMIN_HOME
from lib.utils import common, logutil, util

###### Constants ######
DATE_SEG = 0
YEAR = 0
MONTH = 1
DATE = 2

TIME_SEG = 1
HH = 0
MM = 1
SS = 2

# for zipped files
COLLECTINFO_DIR = ADMIN_HOME + 'collectinfo/'
COLLECTINFO_INTERNAL_DIR = "collectinfo_analyser_extracted_files"

######################


class CollectinfoLoghdlr(object):
    all_cinfo_logs = {}
    selected_cinfo_logs = {}

    def __init__(self, cinfo_path):
        self.cinfo_path = cinfo_path
        self.collectinfo_dir = COLLECTINFO_DIR + str(os.getpid())
        self._validate_and_extract_compressed_files(cinfo_path, dest_dir=self.collectinfo_dir)
        self.cinfo_timestamp = None

        self.reader = CollectinfoReader()
        try:
            self._add_cinfo_log_files(cinfo_path)
        except Exception as e:
            self.close()
            raise e

    def __str__(self):
        status_str = ""
        if not self.all_cinfo_logs:
            return status_str

        i = 1
        for timestamp in sorted(self.all_cinfo_logs.keys()):
            nodes = list(self.all_cinfo_logs[timestamp].get_node_names().keys())
            if len(nodes) == 0:
                continue

            status_str += "\n " + str(i) + ": "
            status_str += ntpath.basename(self.all_cinfo_logs[timestamp].cinfo_file)
            status_str += " ("
            status_str += str(timestamp)
            status_str += ")"
            status_str += "\n\tFound %s nodes" % (len(nodes))
            status_str += "\n\tOnline:  %s" % (", ".join(nodes))
            status_str += "\n"
            i = i + 1

        return status_str

    def close(self):
        if self.all_cinfo_logs:
            for timestamp in self.all_cinfo_logs:
                try:
                    self.all_cinfo_logs[timestamp].destroy()
                except Exception:
                    pass
            self.all_cinfo_logs.clear()
            self.selected_cinfo_logs.clear()

        if os.path.exists(self.collectinfo_dir):
            shutil.rmtree(self.collectinfo_dir)

    def get_cinfo_log_at(self, timestamp=""):

        if not timestamp or timestamp not in self.all_cinfo_logs:
            return None

        return self.all_cinfo_logs[timestamp]

    def info_getconfig(self, stanza="", flip=False):
        return self._fetch_from_cinfo_log(type="config", stanza=stanza, flip=flip)

    def info_get_originalconfig(self, stanza="", flip=False):
        return self._fetch_from_cinfo_log(type="original_config", stanza=stanza, flip=flip)

    def info_statistics(self, stanza="", flip=False):
        return self._fetch_from_cinfo_log(type="statistics", stanza=stanza, flip=flip)

    def info_histogram(self, stanza="", byte_distribution=False, flip=False):
        if byte_distribution and stanza == "objsz":
            stanza = "object-size"

        hist_dict = self._fetch_from_cinfo_log(type="histogram", stanza=stanza, flip=flip)
        res_dict = {}

        version = self.info_meta_data(stanza="asd_build")

        for timestamp, hist_snapshot in list(hist_dict.items()):
            res_dict[timestamp] = {}
            if not hist_snapshot:
                continue

            for node, node_snapshot in list(hist_snapshot.items()):
                res_dict[timestamp][node] = {}
                if not node_snapshot:
                    continue

                for namespace, namespace_snapshot in list(node_snapshot.items()):
                    if not namespace_snapshot:
                        continue

                    try:
                        as_version = version[timestamp][node]
                        d = common.parse_raw_histogram(stanza, namespace_snapshot, logarithmic=byte_distribution,
                            new_histogram_version=common.is_new_histogram_version(as_version))
                        if d and not isinstance(d, Exception):
                            res_dict[timestamp][node][namespace] = d

                    except Exception:
                        pass
        return res_dict

    def info_latency(self):
        return self._fetch_from_cinfo_log(type="latency")

    def info_meta_data(self, stanza=""):
        return self._fetch_from_cinfo_log(type="meta_data", stanza=stanza)

    def info_pmap(self):
        return self._fetch_from_cinfo_log(type="pmap")

    def info_namespaces(self):
        return self._fetch_from_cinfo_log(type="config", stanza="namespace_list")

    def get_sys_data(self, stanza=""):
        res_dict = {}
        if not stanza:
            return res_dict

        for timestamp in sorted(self.selected_cinfo_logs.keys()):
            try:
                out = self.selected_cinfo_logs[timestamp].get_sys_data(stanza=stanza)
                res_dict[timestamp] = util.restructure_sys_data(out, stanza)
            except Exception:
                continue

        return res_dict

    def _get_valid_files(self, cinfo_path=""):
        try:
            if not cinfo_path:
                cinfo_path = self.cinfo_path

            log_files = logutil.get_all_files(cinfo_path)
            valid_files = []
            for log_file in log_files:
                try:
                    if self.reader.is_cinfo_log_file(log_file):
                        valid_files.append(log_file)
                        continue
                except Exception:
                    pass

                try:
                    # ToDo: It should be some proper check for asadm
                    # collectinfo json file.
                    if os.path.splitext(log_file)[1] == ".json":
                        valid_files.append(log_file)
                        continue
                except Exception:
                    pass

                try:
                    if self.reader.is_system_log_file(log_file):
                        valid_files.append(log_file)
                        continue
                except Exception:
                    pass

                try:
                    # ToDo: It should be some proper check for asadm
                    # conf file.
                    if os.path.splitext(log_file)[1] == ".conf":
                        valid_files.append(log_file)
                except Exception:
                    pass

            return valid_files

        except Exception:
            return []

    def _get_all_file_paths(self, cinfo_path):
        files = []

        if os.path.isfile(cinfo_path):
            if not self._is_compressed_file(cinfo_path):
                files.append(cinfo_path)
            else:
                files += logutil.get_all_files(self.collectinfo_dir)

        elif os.path.isdir(cinfo_path):
            files += logutil.get_all_files(cinfo_path)
            if os.path.exists(self.collectinfo_dir):
                # ToDo: Before adding file from collectinfo_dir, we need to check file already exists in input file list or not,
                # ToDo: collectinfo_parser fails if same file exists twice in input file list. This is possible if input has zip file and
                # ToDo: user unzipped it but did not remove zipped file, in that case collectinfo-analyser creates new unzipped file,
                # ToDo: which results in two copies of same file (one unzipped by user and one unzipped by collectinfo-analyser).

                files += self._get_valid_files(self.collectinfo_dir)

        return files

    def _add_cinfo_log_files(self, cinfo_path=""):

        if not cinfo_path:
            raise Exception("Collectinfo path not specified.")

        if not os.path.exists(cinfo_path):
            raise Exception("Wrong Collectinfo path.")

        files = self._get_all_file_paths(cinfo_path)
        if not files:
            raise Exception("No valid Aerospike collectinfo log available.")

        cinfo_log = CollectinfoLog(cinfo_path, files, self.reader)
        self.selected_cinfo_logs = cinfo_log.snapshots
        self.all_cinfo_logs = cinfo_log.snapshots
        snapshots_added = len(self.all_cinfo_logs)
        if not snapshots_added:
            raise Exception("Multiple snapshots available without JSON dump.")

    def _fetch_from_cinfo_log(self, type="", stanza="", flip=False):
        res_dict = {}

        if not type:
            return res_dict

        for timestamp in sorted(self.selected_cinfo_logs.keys()):
            try:
                out = self.selected_cinfo_logs[timestamp].get_data(type=type, stanza=stanza)
                if flip:
                    out = util.flip_keys(out)

                res_dict[timestamp] = out

            except Exception:
                continue

        return res_dict

    def _is_compressed_file(self, file):
        if not file or not os.path.exists(file):
            return False

        if zipfile.is_zipfile(file) or tarfile.is_tarfile(file):
            return True

        return False

    def _extract_to(self, file, dest_dir):
        if not file or not os.path.exists(file):
            return False

        try:
            if tarfile.is_tarfile(file):
                compressed_file = tarfile.open(file)

            elif zipfile.is_zipfile(file):
                compressed_file =  zipfile.ZipFile(file, "r")

            else:
                return False

        except Exception:
            return False

        file_extracted = False
        try:
            compressed_file.extractall(path=dest_dir)
            file_extracted = True
        except Exception:
            file_extracted = False
        finally:
            compressed_file.close()

        return file_extracted

    def _validate_and_extract_compressed_files(self, cinfo_path, dest_dir=None):
        if not cinfo_path or not os.path.exists(cinfo_path):
            return

        if not dest_dir:
            dest_dir = self.collectinfo_dir

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        if os.path.isfile(cinfo_path):
            if not self._is_compressed_file(cinfo_path):
                return

            if self._extract_to(cinfo_path, dest_dir):
                self._validate_and_extract_compressed_files(dest_dir, dest_dir=os.path.join(dest_dir, COLLECTINFO_INTERNAL_DIR))
                return

        files = logutil.get_all_files(cinfo_path)
        if not files:
            return

        file_extracted = False
        for file in files:
            if not self._is_compressed_file(file):
                continue

            if self._extract_to(file, dest_dir):
                file_extracted = True

        if file_extracted:
            self._validate_and_extract_compressed_files(dest_dir, dest_dir=os.path.join(dest_dir, COLLECTINFO_INTERNAL_DIR))


