## Project layout

    Stress-test-router
        .github/
            workflows/
                ci.yml
        docs/
            docs/
                index.md  # The documentation homepage.
            mkdocs.yml    # The configuration file.
        features/
            steps/
                background_steps.py
                client_creation_steps.py
                connectivity_steps.py
                download_steps.py
                google_ping_steps.py
                verify_ip_steps.py
            create_client.feature
            google_ping.feature
            parallel_download.feature
            environment.py
        src/
            client_manager.py
            download_manager.py
            ping_manager.py
        utils/
            command_runner.py
            logger.py
            pi_health_check.py
        .flake8
        .gitignore
        config.yaml
        README.md
        requirements.txt

