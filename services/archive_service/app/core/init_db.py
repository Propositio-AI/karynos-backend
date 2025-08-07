# Create Sample DB Data

def init_archive_type_table():
    from core.db import session
    from models.ArchiveTypeTable import ArchiveTypeTable
    from schemas.ArchiveTypeSchema import ArchiveTypeSchema

    archive_type_data = [
        {
            "type": "TEXTBOOK"
        },
        {
            "type": "GRAPH"
        },
        {
            "type": "CHAT"
        },
    ]

    for data in archive_type_data:
        new_archive_type = ArchiveTypeTable(**ArchiveTypeSchema(**data).model_dump())
        session.add(new_archive_type)
        session.commit()

def init_archive_share_type_table():
    from core.db import session
    from models.ShareTypeTable import ShareTable
    from schemas.ShareTypeSchema import ShareTypeSchema

    archive_type_data = [
        {
            "type": "PRIVATE"
        },
        {
            "type": "PUBLIC"
        },
    ]

    for data in archive_type_data:
        new_archive_type = ShareTable(**ShareTypeSchema(**data).model_dump())
        session.add(new_archive_type)
        session.commit()
