# Create Sample DB Data

# Initialize the Query Type Table Data
def init_query_type_data():
    from core.db import session
    from models.QueryTypeTable import QueryTypeTable
    from schemas.QueryTypeSchema import QueryTypeTableSchema

    original_query_type_data = [
        {
            "type": "TEXTBOOK"
        },
        {
            "type": "CHAT"
        }
    ]

    for data in original_query_type_data:
        new_query = QueryTypeTable(**QueryTypeTableSchema(**data).model_dump())
        session.add(new_query)
        session.commit()