from pandadoc import PandaDocClient

def generate_contract(template_id: str, data: dict, api_key: str) -> dict:
    client = PandaDocClient(api_key)
    return client.create_document_from_template(template_id, data)
