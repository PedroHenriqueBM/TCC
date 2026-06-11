
class Policy:

    def __init__(
            self, 
            governance: str,
            transparency_and_explainability: str,
            justice_and_mitigation_of_bias: str,
            safety_and_robustness: str,
            privacy_and_data_protection: str
    ):
        self.set_governance(governance)
        self.set_transparency_and_explainability(transparency_and_explainability)
        self.set_justice_and_mitigation_of_bias(justice_and_mitigation_of_bias)
        self.set_safety_and_robustness(safety_and_robustness)
        self.set_privacy_and_data_protection(privacy_and_data_protection)
        
    def get_governance(self):
        return self.governance
    def set_governance(self, new_governance:str):
        self.governance = new_governance

    def get_transparency_and_explainability(self):
        return self.transparency_and_explainability
    def set_transparency_and_explainability(self,new_transparency_and_explainability:str):
        self.transparency_and_explainability = new_transparency_and_explainability

    def get_justice_and_mitigation_of_bias(self):
        return self.justice_and_mitigation_of_bias
    def set_justice_and_mitigation_of_bias(self,new_justice_and_mitigation_of_bias:str):
        self.justice_and_mitigation_of_bias = new_justice_and_mitigation_of_bias

    def get_safety_and_robustness(self):
        return self.safety_and_robustness
    def set_safety_and_robustness(self,new_safety_and_robustness: str):
        self.safety_and_robustness = new_safety_and_robustness

    def get_privacy_and_data_protection(self):
        return self.privacy_and_data_protection
    def set_privacy_and_data_protection(self, new_privacy_and_data_protection: str):
        self.privacy_and_data_protection = new_privacy_and_data_protection

    def get_all_components(self):

        return self.get_governance() + self.get_transparency_and_explainability() + self.get_justice_and_mitigation_of_bias() + self.get_safety_and_robustness() + self.get_privacy_and_data_protection()


    