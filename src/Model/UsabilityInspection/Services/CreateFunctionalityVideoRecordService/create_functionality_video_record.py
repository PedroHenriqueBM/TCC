from Model.UsabilityInspection.Exceptions.Functionality.FunctionalityNotExists import FunctionalityNotExists
from Model.UsabilityInspection.Exceptions.Functionality.FuncionalityHasNotUrl import FunctionalityHasNotUrl

from Model.UsabilityInspection.Services.GetPathToSaveVideoService.get_path_to_save_video import get_path_to_save_video
from Model.UsabilityInspection.Services.CheckIfFunctionalityExistsService.check_if_functionality_exists import check_if_functionality_exists
from Model.UsabilityInspection.Services.GetFunctionalityByIdService.get_functionality_by_id import get_functionality_by_id
from Model.UsabilityInspection.Services.RecordVideoService.record_video import record_video

def create_functionality_video_record(functionality_id: str):

        funcionality_exists = check_if_functionality_exists(functionality_id)

        if not funcionality_exists:
            raise FunctionalityNotExists(f"The functionality with {functionality_id} id not exists")

        functionality = get_functionality_by_id(functionality_id)

        url_to_search = functionality.get_url()

        if not url_to_search:
              raise FunctionalityHasNotUrl(f"The functionality with {functionality_id} has not url to record")

        path_to_save_video = get_path_to_save_video(functionality_id)

        path_when_file_was_storage = record_video(path_to_save_video, url_to_search, functionality_id=functionality_id)

        return path_when_file_was_storage

         

        



   



