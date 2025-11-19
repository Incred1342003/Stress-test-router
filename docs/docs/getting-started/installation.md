## Setup Process

* `git clone https://github.com/panditpankaj21/Stress-test-router.git` - Clone the repo.
* `cd Stress-test-router` - Go to main directory.
* `pip install -r requirements.txt` - Install the dependencies using file requirements.txt
* `sudo behave` - To run all the features in one go.
* `sudo behave features/<name_of_feature.feature>` - Run the specific feature
* `sudo behave --tags="@tag_name"` - Run the specific Senario using tag


## Docs

* `cd docs` - Go to docs directory
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.
