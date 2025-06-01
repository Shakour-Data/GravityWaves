import os
import subprocess

def run_tests_sequentially(tests_dir='tests', log_file='test_results/test_output.log'):
    # Clear previous log file
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w') as f:
        f.write('Test run started\\n\\n')

    # List test files
    test_files = sorted(
        f for f in os.listdir(tests_dir)
        if f.startswith('test_') and f.endswith('.py')
    )

    for test_file in test_files:
        test_path = os.path.join(tests_dir, test_file)
        print(f'Running tests in {test_path}...')
        with open(log_file, 'a') as f:
            f.write(f'Running tests in {test_path}\\n')
            f.write('-' * 40 + '\\n')

        # Run pytest on the test file
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        result = subprocess.run(
            ['pytest', test_path, '--tb=short', '-q'],
            capture_output=True,
            text=True,
            env=env
        )

        # Append output to log file
        with open(log_file, 'a') as f:
            f.write(result.stdout)
            f.write(result.stderr)
            f.write('\\n')

        # Print summary to console
        if result.returncode == 0:
            print(f'Tests passed in {test_path}')
            with open(log_file, 'a') as f:
                f.write(f'Tests passed in {test_path}\\n\\n')
        else:
            print(f'Tests failed in {test_path}. Stopping further tests.')
            with open(log_file, 'a') as f:
                f.write(f'Tests failed in {test_path}. Stopping further tests.\\n')
            break

    print(f'Test run complete. See {log_file} for details.')

if __name__ == '__main__':
    run_tests_sequentially()
