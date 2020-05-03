# Sample etl pipeline
This project is a simple etl pipeline that takes data from the Danish Maritime Authority. 
Source data can be found [here](ftp://ftp.ais.dk/ais_data/).

The pipeline detailed here follows a simple Read ⇒ Validate ⇒ Load pattern.
This pattern is suitable for data that is coming from a consistent source and requires minimal business logic to be applied before delivery to storage.

## How to run
This project requires:
Docker - [download here](https://www.docker.com/products/docker-desktop) & a docker-hub account.

**Accessing data**
Test data can be downloaded from the Danish AIS repo manually or by using `wget ftp://ftp.ais.dk/ais_data/aisdk_20181101.csv` (other files are also available) from the data source. Most files are ~2GB in size. 
Optionally, you may want to subset the data in order to run the process more quickly. Currently the process relies on the presence of a header so only the top N rows should be taken, not rows from within the middle of the file.
Use `head -10 <file_name> > <output_file>` to easily select the first 10 rows from a csv and write them to a new file.

**Setting up docker**
This project uses a Postgres database hosted in a docker container as it's DB of choice. Once you have docker installed and a docker-hub account set up you can run the following command to set-up a postgres database listening port 5432 of your localhost.
`docker run --rm -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres`

**Running the pipeline**
For running the pipeline, it is recommended to set up a virtual environment with the packages listed in the `requirements.txt` file installed. 
(**N.B:** this work has currently only been tested with python 3.6.9 although I don't foresee any major issues with running any python 3.x version.)

The pipeline can be run by invoking the main.py file which expects 2 arguments with an optional 3rd:
`--file-path <path to input data>`
`--sql <url of sql instance>`
Optional `--loader <loader to use to access data>` defaults to "local"

The for this project `--sql postgresql://postgres:postgres@localhost:5432` can be used and the pipeline will run successfully.

Only the "local" loader has been implemented at present so omitting this option has no impact.

## Output
This system outputs 2 sql tables: "ais_denmark" and "ais_denmark_report".
- "ais_denmark" contains the information provided within the downloaded csv as well as a timestamp that can be uses to join the data with it's report.
- "ais_denmark_report" contains information on the number of unique values for each categorical field that was ingested as well as a total count of missing values within the table. There is also a timestamp which can be used to join onto the "ais_denmark" table in order to subset data ingested in this run.

The system also outputs a table of invalid values, this csv contains all the rows that were rejected by the validation step. Having these values output allows users to evaluate these rows and change their validation criteria or discard them and report them to the data producer. For this work the validation criteria were very lax, only checking expected data types so this output is usually empty.

## Future work

Logging to go alongside the output report table and invalid data would be the next thing I would be looking to add. Having these logs are valuable when doing long running ingestion jobs to spot issues early on in the run. They also become invaluable when moving to a streaming system where your validation steps can be highly distributed.

As more data is stored in the database there would be requirements to begin adding data models that would allow both for efficient storage of the data and the combining of data sets from disparate sources.

Given that the data provided for this project was already structured, there was minimal transformation that needed to be applied. In order to make this process robust to other delivery methods (json, parquet etc) there needs to be some extension of the main pipeline.