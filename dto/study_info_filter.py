from fastapi import Query

class QueryUserDataFilterByPassport:
    def __init__(
        self,
        passport_series_number: str = Query(None),
        jshshir: str = Query(None),
        first_name: str = Query(None),
        last_name: str = Query(None),
        third_name: str = Query(None),
        region: str = Query(None),
        gender: str = Query(None),
    ):
        self.passport_series_number = passport_series_number
        self.jshshir = jshshir
        self.first_name = first_name
        self.last_name = last_name
        self.third_name = third_name
        self.region = region
        self.gender = gender


class QueryUserDataFilterByStudy:
    def __init__(
        self,
        study_language: str = Query(None),
        study_form: str = Query(None),
        study_direction_name: str = Query(None),
        education_type: str = Query(None),
        study_type: str = Query(None),
    ):
        self.study_language = study_language
        self.study_form = study_form
        self.study_direction_name = study_direction_name
        self.education_type = education_type
        self.study_type = study_type
