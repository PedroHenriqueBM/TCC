import os

def get_path_to_save_video(functionality_id: str):
    path = os.path.join(os.getcwd(),"src","Storage",f'{functionality_id}')
    return path

