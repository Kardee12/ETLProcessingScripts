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
    def to_csv(data, filename):
        fieldnames = list(data[0].keys())
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)
