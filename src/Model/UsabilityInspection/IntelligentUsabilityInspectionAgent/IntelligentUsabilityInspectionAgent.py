from Model.UsabilityInspection.IntelligentUsabilityInspectionAgent.Policy import Policy
from Model.UsabilityInspection.Functionality.Functionality import Funcionality
from Model.UsabilityInspection.IntelligentUsabilityInspectionAgent.UsabilityHeuristicDatabase.UsabilityHeuristicDatabase import UsabilityHeuristicDatabase
from Model.UsabilityInspection.Exceptions.Policy.PolicyMissing import PolicyMissing
from Model.UsabilityInspection.Exceptions.Functionality.FunctionalityMissing import FunctionalityMissing
import re


class IntelligentUsabilityInspectionAgent:

    def __init__(
        self,
        policy: Policy = None,
        usability_heuristic_database: UsabilityHeuristicDatabase = None,
        functionality: Funcionality = None
    ):
        self.policy: Policy = policy
        self.usability_heuristic_database: UsabilityHeuristicDatabase = usability_heuristic_database
        self.functionality: Funcionality = functionality
        
    def consults_policy(self, policy: Policy):
        self.policy = policy
    
    def consults_usability_heuristic_database(self, usability_heuristic_database: UsabilityHeuristicDatabase):
        self.usability_heuristic_database = usability_heuristic_database

    def analisys_functionality(self, functionality: Funcionality):
        self.functionality = functionality

    def get_system_prompt(self):

        if not self.policy:
            raise PolicyMissing("Usability policy is missing on agent")

        system_prompt = self.compact_text(self.policy.get_all_components())
        return system_prompt
    
    def get_user_prompt(self):

        if not self.functionality:
            raise FunctionalityMissing("Functionality is missing on agent")

        user_prompt = self.compact_text(f'''
            Funcionalidade: {self.functionality.get_description()}
            Critério de aceite: {self.functionality.get_acceptance_criteria()}
            Comentários anteriores: {self.functionality.get_comments()}
        ''')
        return user_prompt

    def compact_text(self,text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()