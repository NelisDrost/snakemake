import os
from pathlib import Path
import sys
import tempfile

from google.cloud import storage

sys.path.insert(0, Path(__file__).parent.parent)

from common import *


def has_google_credentials():
    return "GOOGLE_APPLICATION_CREDENTIALS" in os.environ


google_credentials = pytest.mark.skipif(
    not has_google_credentials(),
    reason="Skipping google lifesciences tests because  "
    "GOOGLE_APPLICATION_CREDENTIALS not found in the environment.",
)


def cleanup_google_storage(prefix, bucket_name="snakemake-testing", restrict_to=None):
    """Given a storage prefix and a bucket, recursively delete files there
    This is intended to run after testing to ensure that
    the bucket is cleaned up.

    Arguments:
      prefix (str) : the "subfolder" or prefix for some files in the buckets
      bucket_name (str) : the name of the bucket, default snakemake-testing
      restrict_to (list) : only delete files in these paths (None deletes all)
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="source")
    for blob in blobs:
        blob.delete()
    blobs = bucket.list_blobs(prefix=prefix)
    for blob in blobs:
        if restrict_to is None or f"{bucket_name}/{blob.name}" in restrict_to:
            blob.delete()
    if restrict_to is None:
        # Using API we get an exception about bucket deletion
        shell("gsutil -m rm -r gs://{bucket.name}/* || true")
        bucket.delete()


def create_google_storage(bucket_name="snakemake-testing"):
    """Given a bucket name, create the Google storage bucket,
    intending to be used for testing and then cleaned up by
    cleanup_google_storage

    Arguments:
      bucket_name (str) : the name of the bucket, default snakemake-testing
    """
    client = storage.Client()
    return client.create_bucket(bucket_name)


def get_temp_bucket_name():
    return "snakemake-testing-%s-bucket" % next(tempfile._get_candidate_names())