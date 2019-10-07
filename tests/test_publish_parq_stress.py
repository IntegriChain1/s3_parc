import pytest
from dfmock import DFMock
import boto3
from moto import mock_s3
import s3parq.publish_parq as pub_parq

# generates single partition path files of compressed size ~60mb

# @pytest.mark.skip(reason="skip to speed up tests")


@mock_s3
def test_parquet_sizes():
    bucket = "testbucket"
    key = "testdataset"
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket=bucket)
    df = DFMock(count=1000)
    df.columns = {"int_col": "int", "str_col": "string",
                  "grouped_col": {"option_count": 4, "option_type": "string"}}
    df.generate_dataframe()
    df.grow_dataframe_to_size(250)
    pub_parq.publish(
        dataframe=df.dataframe, key=key, bucket=bucket, partitions=['grouped_col'])

    for obj in s3_client.list_objects(Bucket=bucket)['Contents']:
        if obj['Key'].endswith(".parquet"):
            assert float(obj['Size']) <= 61 * float(1 << 20)
