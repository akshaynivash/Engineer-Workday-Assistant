# test_tasks.py
import tasks

def test_database_functions():
    table_name = "daily_tasks_test"

    # 1. Create table
    creation_status = tasks.create_table_if_not_exists(table_name)
    print("Table Creation Status:", creation_status)

    # 2. Insert a sample record
    task_item = "Take vitamins"
    answer_item = "Yes, I took them."
    insert_status = tasks.save_task_response(table_name, task_item, answer_item)
    print("Insert Status:", insert_status)

if __name__ == "__main__":
    test_database_functions()
