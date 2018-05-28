import os

from rlbot.agents.base_independent_agent import BaseIndependentAgent
from rlbot.botmanager.helper_process_request import HelperProcessRequest


class ScratchBot(BaseIndependentAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)

    def get_helper_process_request(self):
        file = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scratch_manager.py'))
        key = 'scratch_helper'
        return HelperProcessRequest(file, key)

    def run_independently(self, terminate_request_event):
        pass
