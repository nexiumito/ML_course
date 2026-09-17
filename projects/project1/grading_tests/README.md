# Helper for grading project 1


Files to give to the students:

```
conftest.py
test_project1_public.py
INSTRUCTIONS.md
environment.yml
```

Run in this directory:

```
pytest --github_link <GITHUB-REPO-URL> .
```

## Extra dependencies

```
pip install black pytest-csv pytest-mock plydata
```

```
sudo apt-get install parallel
```

## Grading in batch

Export the submissions from hotCRP in json format and use `jq` to post-process them.

Check the Github repos: 
```
cat crpmlcourse-data.json | jq --raw-output '.[]  | "\(.pid) \(.code_github_link)"'
```

`| grep -v CS-433` and `grep -v /tree/` are useful filters.


Create the pytest commands in a file:

```
cat crpmlcourse-data.json | jq --raw-output '.[]  | "pytest --use_ssh --github_link \(.code_github_link) --clone_directory ~/repos/\(.pid) --csv ~/results/\(.pid).csv --keep_repo . >> ~/results/\(.pid)_pytest"'
```

Add manualy the commit explicitly with the `--commit_hash` flag for the repos that don't have the right format.

```
mkdir -p ~/results/ ~/repos/
cat commands | parallel --bar -- {}
```

Post-process results in one CSV file `results.csv`:

```
python post_process.py results
```

### Setup a VM on GCP

You should run the test on a VM at least for two reasons: more CPUs and more security (it will run students code).
```
sudo apt-get install git parallel jq wget locales
```

As root:
```
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
```

Follow [the instructions](https://linuxize.com/post/how-to-install-anaconda-on-debian-10/) to install conda, run `anaconda3/bin/conda init`, restart your shell.


## Plagiarsism check

Transform each repo into a single Python file:

```
ls -d ~/repos/* | parallel --bar python directory_to_single_python_file.py {}
```

You can create a base file with the public code in the ML_course repo in the same way.

Then run the MOSS script:

```
./moss.pl -b ~/ML_course.py -m 10 -l python <ONE_PYTHON_FILE_PER_GROUP>
```

## 2024 Update
The students make their main submissions at [mlcourse.epfl.ch](mlcourse.epfl.ch).

First obtain the submission information for each group:
- Go to mlcourse.epfl.ch
- Search all in submitted (no keywords)
- Select all the relevant submissions, order by ID, shift click to select all relevant submissions. Note you may need to be a chair in order to be able to see all submissions. You may also see older submissions from previous courses or years, make sure to only select the relevant (recent) ones.
- Scroll to the bottom of the search results, click download, select JSON, then click GO
- The JSON file, `mlcourse-data.json`, is in the following format (one example shown):
```
[
    {
        "pid": 595,
        "title": "Project1",
        "submission": {
            "mimetype": "application\/pdf",
            "hash": "sha2-fa8d8c137cd898ef142d83346c05753e51c8b945296a24809d342e836dfcef5a",
            "timestamp": 1730473216,
            "size": 210760
        },
        "abstract": "",
        "authors": [
            {
                "email": "first.last@epfl.ch",
                "first": "FirstName",
                "last": "LastName",
                "affiliation": "EPFL"
            },
            {
                "email": "first.last@epfl.ch",
                "first": "FirstName",
                "last": "LastName",
                "affiliation": "EPFL"
            }
        ],
        "contacts": [
            {
                "email": "first.last@epfl.ch",
                "first": "FirstName",
                "last": "LastName",
                "affiliation": "EPFL"
            }
        ],
        "github_code_link": "https:\/\/github.com\/CS-433\/ml-project-1-some-name.git\/commit\/244bb67d",
        "aicrowd_username_submission_id": "Name, ID: 274402",
        "topics": [
            "Project 1"
        ],
        "status": "submitted",
        "submitted": true,
        "submitted_at": 1730473216
    }
]
```

Get a linux machine on GCP, RCP, IC Cluster or similar. This machine will be running student code so note the security implications.
- Install the required packages: `sudo apt-get update`, `sudo apt-get install git parallel jq wget locales`.
- Install conda:
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm ~/miniconda3/miniconda.sh
source ~/miniconda3/bin/activate
```
- Set up your Github access and clone the private repo (note that this is potentially insecure for running student code).
- `cd ML_course_private/projects/project1/grading_tests`
- Create and activate the test environment: `conda env create --file=environment.yml --name=project1-grading`, `conda activate project1-grading`
- Move `mlcourse-data.json` to the machine (e.g. scp or just paste it into vim)
- View a list of the Github repos: `cat mlcourse-data.json | jq --raw-output '.[]  | "\(.pid) \(.github_code_link)"'`. Some might not have submitted classroom repos, some might have obvious errors in the url (like duplicate https).
- Create the commands to test the repos: `cat mlcourse-data.json | jq --raw-output '.[]  | "pytest --timeout=60 --use_ssh --github_link \(.github_code_link) --clone_directory ~/repos/\(.pid) --csv ~/results/\(.pid).csv --keep_repo . >> ~/results/\(.pid)_pytest"' >> run_commands.sh`
- You might have to fix some of the github links manually. This year many students submitted invalid URLs that can not be checked out directly.
- Create the necessary directories: `mkdir -p ~/results/ ~/repos/`
- `pip install black pytest-csv pytest-mock plydata pytest-timeout`
- Run the tests in parallel with `cat run_commands.sh | parallel --bar -- {}`
- Gather the results: `python post_process.py ~/results --repos_dir ~/repos --deadline "2024-11-01T16:05:00+01:00"`
- The results should be in: `~/results.csv`