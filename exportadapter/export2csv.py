# -*- coding: utf-8 -*-
# Written for Python 3.4
import csv
from sdsct.exportadapter.export2generic import Export2Generic
# TODO: use csv

class Export2Csv(Export2Generic):

    file_name = 'python2cxt.csv'
    delimiter_default = '\t'
    file_name_default_extension = 'txt'  # TODO: use if no extension given.
    header_included = True

    def export(self, result, file_name=None, output_directory=None, header_included=None):
        delimiter = self.delimiter_default
        header_included = self.header_included if header_included is None else header_included
        if output_directory:
            output_directory = self._clean_path(output_directory)
        else:
            output_directory = self.output_directory
        file_name = file_name or self.file_name

        if len(file_name.split('.')) == 1:  # missing file extension   # TODO pull up to superclass
            file_name += '.'+self.file_name_default_extension
        if self.timestamp_included:
            file_name_trunc, file_name_extension = file_name.split('.')
            file_name = file_name_trunc+'_'+self._get_timestamp_string()+'.'+file_name_extension

        file_name = '/'.join((output_directory, file_name))

        with open(file_name, 'w', newline='', encoding='utf8') as f:
            if result:
                writer = csv.writer(f, delimiter=delimiter)
                if isinstance(result[0], dict):
                    keys = result[0].keys()
                    if header_included:
                        writer.writerow(list(keys))
                    result = [[row[key] for key in keys] for row in result]
                    writer.writerows(result)
                else:
                    if header_included and hasattr(result[0], '_fields'):  # header for named tuples,
                        writer.writerow([str(element) for element in getattr(result[0], '_fields')])
                    writer.writerows(result)
