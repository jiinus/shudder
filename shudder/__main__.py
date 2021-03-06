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

"""Start polling of SQS and metadata."""
import shudder.queue as queue
import shudder.metadata as metadata
from shudder.config import CONFIG, LOG_FILE
import time
import os
import requests
import signal
import subprocess
import sys
import logging
from requests.exceptions import ConnectionError

logging.basicConfig(filename=LOG_FILE,format='%(asctime)s %(levelname)s:%(message)s',level=logging.INFO)


def receive_signal(signum, stack):
    if signum in [1,2,3,15]:
        logging.exception('Caught signal %s, exiting.' %(str(signum)))
        sys.exit(0)
    else:
        logging.exception('Caught signal %s, ignoring.' %(str(signum)))

if __name__ == '__main__':
    uncatchable = ['SIG_DFL','SIGSTOP','SIGKILL']
    for i in [x for x in dir(signal) if x.startswith("SIG")]:
        if not i in uncatchable:
            signum = getattr(signal,i)
            signal.signal(signum,receive_signal)

    sqs_connection, sqs_queue = queue.create_queue()
    sns_connection, subscription_arn = queue.subscribe_sns(sqs_queue)
    while True:
      try:
        message = queue.poll_queue(sqs_connection, sqs_queue)
        if message or metadata.poll_instance_metadata():
            if 'endpoint' in CONFIG:
                requests.get(CONFIG["endpoint"])
            if 'endpoints' in CONFIG:
                for endpoint in CONFIG["endpoints"]:
                    requests.get(endpoint)
            if 'commands' in CONFIG:
                for command in CONFIG["commands"]:
                    logging.info('Running command: %s' % command)
                    process = subprocess.Popen(command)
                    time.sleep(15)
                    while process.poll() is None:
                        """Send a heart beat to aws"""
                        queue.record_lifecycle_action_heartbeat(message)
                        time.sleep(30)
            """Send a complete lifecycle action"""
            queue.complete_lifecycle_action(message)
            sys.exit(0)
      except SystemExit:
        logging.info('Exiting, cleaning SNS')
        queue.clean_up_sns(sns_connection, subscription_arn, sqs_queue)
        break
      except ConnectionError:
        logging.exception('Connection issue')
      except:
        logging.exception('Something went wrong')
      finally:
        time.sleep(5)