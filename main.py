from typing import List
import datetime as dt
import pandas as pd
import sqlalchemy
import click
import loaders
import validator


def process_ais(df) -> pd.DataFrame:
    """Specific processing for the AIS data to handle col names with white space and
    datetime columns in odd formats.
    """
    ais_df = df.copy()
    ais_df.columns = [i.lower().replace(" ", "_").replace('#_', '') for i in ais_df.columns]
    ais_df.timestamp = pd.to_datetime(ais_df.timestamp)
    ais_df.eta = pd.to_datetime(ais_df.eta)
    return ais_df


def _get_str_cols(df) -> List[str]:
    is_object = [i == "O" for i in df.dtypes]
    object_cols = list(df.columns[is_object])
    return object_cols


def _count_unique(df, col_name) -> int:
    return len(df[col_name].unique())


def count_unique_str_cols(df) -> pd.DataFrame:
    str_cols = _get_str_cols(df)

    data = {}

    for col in str_cols:
        data.update(
            {
                f"{col}_count_unique_vals": [_count_unique(df, col)],
                f"{col}_unique_vals": [_get_unique_vals(df, col)]
            }
        )

    return pd.DataFrame(data)


def _get_unique_vals(df, col_name) -> List[str]:
    uniques = [str(i) for i in df[col_name].unique()]
    return uniques


def count_nulls(df) -> int:
    return df.isnull().sum().sum()


@click.command()
@click.option('-f', '--file-path', required=True)
@click.option('-l', '--loader', default="local")
@click.option('-s', '--sql', required=True)
def main(file_path, loader, sql):
    now = dt.datetime.now()

    df = loaders.get_csv(file_path, loader)
    df = process_ais(df)

    valid_rows = df.apply(validator.validate, model=validator.AISSchema, axis=1)
    valid_df = df[valid_rows]

    report_unique_counts = count_unique_str_cols(valid_df)
    report_unique_counts['total_nulls'] = [count_nulls(valid_df)]

    sql_engine = sqlalchemy.create_engine(sql)
    valid_df['ingest_ts'] = [str(now)] * len(valid_df)
    report_unique_counts["ingest_ts"] = [str(now)] * len(report_unique_counts)

    with sql_engine.connect() as conn:
        valid_df.to_sql("ais_denmark", conn, if_exists="append", index=False)
        report_unique_counts.to_sql("ais_denmark_report", conn, if_exists="append", index=False)

    invalid_df = df[[not i for i in valid_rows]]
    invalid_df.to_csv(f"logs/{now}-logs.csv")


if __name__ == "__main__":
    main()
