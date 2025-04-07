import random
import os
from datetime import datetime, timedelta

class PatientRecord:
    def __init__(self, records):
        self.records = records
        self.steps = 0

    def bubble_sort(self, key):
        self.steps = 0
        n = len(self.records)
        #use copy to keep original list unsorted to allow for comparisons of multiple sort methods with same data
        sorted_records = self.records.copy() 
        for i in range(n):
            for j in range(0, n - i - 1):
                self.steps += 1
                if sorted_records[j][key] > sorted_records[j + 1][key]:
                    sorted_records[j], sorted_records[j + 1] = sorted_records[j + 1], sorted_records[j]
        return sorted_records

    def merge_sort(self, key):
        """
        Perform a merge sort on self.records based on the given key.
        Returns a sorted copy of the records.
        """
        self.steps = 0
         #use copy to keep original list unsorted to allow for comparisons of multiple sort methods with same data
        return self._merge_sort(self.records.copy(), key)

    def _merge_sort(self, records, key):
        """
        Recursively splits and merges records.
        """
        if len(records) <= 1:
            return records

        mid = len(records) // 2
        left = self._merge_sort(records[:mid], key)
        right = self._merge_sort(records[mid:], key)
        return self._merge(left, right, key)

    def _merge(self, left, right, key):
        """
        Merge two sorted lists 'left' and 'right' based on the given key.
        Counts each comparison in self.steps.
        """
        merged = []
        i, j = 0, 0

        while i < len(left) and j < len(right):
            self.steps += 1
            if left[i][key] <= right[j][key]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        # Append remaining elements from either list
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    def sort_with_metrics(self, method="bubble", key="admission_date"):
        n = len(self.records)
        if method == "bubble":
            sorted_data = self.bubble_sort(key)
        elif method == "merge":
            sorted_data = self.merge_sort(key)
        else:
            raise ValueError("Method must be 'bubble' or 'merge'")
        
        return {
            "n": n,
            "steps": self.steps,
            "key": key,
            "sorted_data": sorted_data,
            "sort_method" : method
    }

def print_sort_results(result):
    GREEN = '\033[92m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    print(f"{BOLD}Sorted {result['n']} records in {result['steps']} steps by key '{result['key']} using {result['sort_method']} sort '.{RESET}")
    print("Sorted Records:")
    
    # for record in result["sorted_data"]:
    #     key = result["key"]
    #     value = record.get(key, "N/A")
    #     colored_value = f"{GREEN}{value}{RESET}"
    #     record_str = ', '.join(
    #         f"{k}: {colored_value if k == key else v}" for k, v in record.items()
    #     )
    #     print(f"{{{record_str}}}")

def generate_random_patients(n):
    first_names = ["Ava", "Liam", "Sophia", "Elijah", "Isabella", "Mateo", "Emily", "Noah", "Mia", "Ethan", "Zoe", "Lucas"]
    last_names = ["Thompson", "Rodriguez", "Patel", "Kim", "Nguyen", "Carter", "Johnson", "Singh", "Lewis", "Martinez", "Brooks", "Clark"]
    
    def random_date(start, end):
        delta = end - start
        return (start + timedelta(days=random.randint(0, delta.days))).strftime('%Y-%m-%d')

    dob_start = datetime(1900, 1, 1)
    dob_end = datetime.today()

    admission_start = datetime(2000, 1, 1)
    admission_end = datetime.today()

    patients = []
    for i in range(n):
        first = random.choice(first_names)
        last = random.choice(last_names)
        record = {
            "patient_id": str(10001 + i),
            "first_name": first,
            "last_name": last,
            "dob": random_date(dob_start, dob_end),
            "admission_date": random_date(admission_start, admission_end)
        }
        patients.append(record)
    
    return patients


if __name__ == "__main__":
    try:
        record_quantity = int(input("Enter number of records to generate: "))
    except ValueError:
        print("Invalid input. Using default value of 10")
        record_quantity = 10
    records = generate_random_patients(record_quantity)
    p_records = PatientRecord(records)
    print_sort_results(p_records.sort_with_metrics("bubble", "last_name"))
    print_sort_results(p_records.sort_with_metrics("merge", "last_name"))
