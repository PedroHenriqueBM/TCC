
class PolicyMissing(Exception):

    def __init__(self, menssage="Policy is missing"):
        super().__init__(menssage)