import plyvel  # type: ignore

import src.data_models as dm

def pull_batch_mapping(config: dm.Config, batch: dm.ResponseBatch) -> dm.BatchMapping:
    """
    Retrieve dm.BatchMapping from database

    Parameters
    ---------
    config:
        Config of database
    batch:
        Response Batch object
    """
    # Open conndection
    try:
        database = plyvel.DB(
            config.db_file,
        )
    except plyvel._plyvel.IOError as exc:
        raise IOError() from exc
    # Pull batch mapping from database
    batch_mapping_bytes = database.get(bytes(batch.uid, "utf-8"))
    batch_mapping = dm.BatchMapping.from_key_value(
        (bytes(batch.uid, "utf-8"), batch_mapping_bytes)
    )

    # Delete mapping
    database.delete(bytes(batch.uid, "utf-8"))
    database.close()

    return batch_mapping