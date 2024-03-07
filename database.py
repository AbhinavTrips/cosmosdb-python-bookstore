
async def getAllBooks(page = 0, limit = 20):
    offset = page * limit
    query_items_response = books_container.query_items(
            query="SELECT c.title, c.author, c.img FROM c  OFFSET @offset LIMIT @limit",
            enable_cross_partition_query=True,
            parameters=[
                dict(
                    name="@offset",
                    value=offset
                ),
                dict(
                    name="@limit",
                    value=limit
                )
            ]
        )
        
    items = []
    for item in query_items_response:
        items.append(item)
    return items

