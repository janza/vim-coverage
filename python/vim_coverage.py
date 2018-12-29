# Copyright 2017 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Python-only helpers for vim-coverage."""

import os
import os.path
import coverage
import glob
import xml.etree.ElementTree as ET


def GetCoveragePyLines(path, source_file):
    """Get (covered, uncovered) lines for source_file from .coverage file at path.
    """
    prev_cwd = os.getcwd()
    source_file = os.path.abspath(source_file)
    try:
        os.chdir(os.path.isfile(path) and os.path.dirname(path) or path)
        try:
            # Coverage.py 4.0 and higher.
            cov = coverage.Coverage()
        except AttributeError:
            cov = coverage.coverage()
        cov.load()
    finally:
        os.chdir(prev_cwd)
    try:
        # Coverage.py 4.0 and higher.
        covered_lines = cov.data.lines(source_file)
    except TypeError:
        covered_lines = cov.data.line_data()[source_file]
    uncovered_lines = cov.analysis(source_file)[2]
    return (covered_lines or [], uncovered_lines)


class FileNotFoundInClover(Exception):
    pass


def get_root(root):
    if root[0][0].tag == 'metrics':
        return root[0][0]
    return root[0]


def loop_files(root):
    for element in get_root(root):
        if element.tag == 'file':
            yield element
        if element.tag == 'package':
            for covered_file in element:
                if covered_file.tag == 'file':
                    yield covered_file


def parse_file(clover_file, source_file):
    covered_lines = []
    uncovered_lines = []
    root = ET.parse(clover_file).getroot()
    for covered_file in loop_files(root):
        file_name = covered_file.attrib.get('path', covered_file.attrib.get('name'))
        if file_name is None:
            print(covered_file)
        if source_file not in file_name:
            continue
        for line in covered_file:
            if line.tag != 'line':
                continue
            if int(line.attrib['count']) > 0:
                covered_lines.append(int(line.attrib['num']))
            else:
                uncovered_lines.append(int(line.attrib['num']))
        return covered_lines, uncovered_lines
    raise FileNotFoundInClover


def GetCoverage(path, source_file):
    files_checked = []
    for clover_file in glob.iglob('**/clover.xml', recursive=True):
        try:
            files_checked.append(clover_file)
            print('Checking {}'.format(clover_file))
            return parse_file(clover_file, source_file)
        except FileNotFoundInClover:
            pass
    print('{} not found in {}'.format(source_file, files_checked))
    return ([], [])
