class ConformityResult:

    def __init__(self, valid: bool, feedback: str):
        self.valid = valid
        self.feedback = feedback

    def __repr__(self):
        status = "VÁLIDO" if self.valid else "INVÁLIDO"
        return f"ConformityResult({status}): {self.feedback}"
