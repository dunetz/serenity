from serenity.data.batch.utils import LoadSharadarTableTask, ExportQuandlTableTask
from serenity.data.sharadar_api import yes_no_to_bool
from serenity.data.sharadar_refdata import UnitType, Indicator


class LoadSharadarMetaTask(LoadSharadarTableTask):
    def requires(self):
        return ExportQuandlTableTask(table_name=self.get_workflow_name())

    def process_row(self, index, row):
        table_name, indicator, is_filter, is_primary_key, title, description, unit_type_code = row
        is_filter = yes_no_to_bool(is_filter)
        is_primary_key = yes_no_to_bool(is_primary_key)

        unit_type = UnitType.get_or_create(self.session, unit_type_code)

        ind_entity = Indicator.find_by_name(self.session, table_name, indicator)
        if ind_entity is None:
            ind_entity = Indicator(table_name=table_name,
                                   indicator=indicator,
                                   is_filter=is_filter,
                                   is_primary_key=is_primary_key,
                                   title=title,
                                   description=description,
                                   unit_type=unit_type)
            self.session.add(ind_entity)

    def get_workflow_name(self):
        return 'SHARADAR/INDICATORS'
