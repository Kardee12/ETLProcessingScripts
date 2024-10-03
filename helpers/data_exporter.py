import csv
import json


class DataExporter:
    @staticmethod
    def to_json(data):
        return [entry.dict() for entry in data]

    @staticmethod
    def json_dump(data, filename):
        with open(filename, 'w') as file:
            json.dump(data, file)

    @staticmethod
    def to_csv(data, file_obj):
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
