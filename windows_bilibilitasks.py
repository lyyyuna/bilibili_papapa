from bilibilitasks import app


if __name__ == "__main__":
    argv = [
        'worker',
		'-c 1',
        '--loglevel=INFO',
    ]
    app.worker_main(argv)