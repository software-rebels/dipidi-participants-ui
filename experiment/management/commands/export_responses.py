import csv

from django.core.management.base import BaseCommand, CommandError
from experiment.models import Response, Participant, Task

import json

class Command(BaseCommand):
    help = "Generate response CSV"

    def handle(self, *args, **options):
        defined_tasks = Task.objects.all()
        columns = ["email", "tooling_level"] + [str(x) for x in defined_tasks]
        id_to_task_map = {x.id: str(x) for x in defined_tasks}
        rows = []
        for participant in Participant.objects.filter(finished_experiment=True):
            tasks = participant.participanttask_set.all()
            row = {x: "NA" for x in columns}
            row["email"] = participant.user.username
            row['tooling_level'] = Participant.TOOLING_CHOICES[int(participant.tooling_level)-1][1]
            for task in tasks:
                if task.is_skipped:
                    row[id_to_task_map[task.task_id]] = "skipped"
                else:
                    result = []
                    for response in task.response_set.all():
                        response = json.loads(response.response)
                        if task.task.task_type == "A" and "deliverable" in response:
                            result.append(response['deliverable'])
                        if task.task.task_type == "B" and "commit_id" in response:
                            result.append(f"{response['commit_id']}:{response['order']}")
                        if task.task.task_type == "C":
                            if "configuration" in response:
                                result.append(f"{response['commit_id']}:{response['configuration']}")
                            elif "affect" in response:
                                result.append(f"{response['commit_id']}:{response['affect']}")
                    row[id_to_task_map[task.task_id]] = ",".join(result)
                rows.append(row)
            with open("result.csv", 'w', newline='') as csv_out:
                writer = csv.DictWriter(csv_out, fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
