from Database.repositories.functional_requirement_repository import functional_requirement_exists


def check_if_functionality_exists(funcionality_id: str) -> bool:
    return functional_requirement_exists(funcionality_id)
