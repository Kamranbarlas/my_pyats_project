import os
print("Initializing parent package")
print("__file__ is:", __file__)  # debug line
def list_test_scripts():
    package_dir = os.path.dirname(os.path.abspath(__file__))
    print("package_dir is:", package_dir)  # debug line

    ordered_tests = [
        # 'test_add_server.py',
        # 'test_delete_server',
        'test_multiple_server.py',
        # 'test_verify_configure_key.py',
        # 'test_verify_key.py'
        # ...
    ]

    full_paths = []
    for test in ordered_tests:
        full_path = os.path.join(package_dir, test)
        print("Checking:", full_path)  # debug line
        if os.path.exists(full_path):
            full_paths.append(full_path)

    return full_paths
