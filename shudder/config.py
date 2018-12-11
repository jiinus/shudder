# Copyright 2014 Scopely, Inc.
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

"""Configuration for shudder"""
import sys
import os
import toml

if len(sys.argv) > 1:
	CONFIG_FILE = sys.argv[1]
else:
	CONFIG_FILE = os.environ.get('CONFIG_FILE', "shudder.toml")

CONFIG = {}

with open(CONFIG_FILE, 'r') as f:
    CONFIG = toml.loads(f.read())
    if 'logfile' in CONFIG.keys():
      LOG_FILE = CONFIG['logfile']
    else:
      LOG_FILE = os.environ.get('LOG_FILE', '/var/log/shudder.log')
