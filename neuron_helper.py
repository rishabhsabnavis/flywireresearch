from fafbseg import flywire
import navis


def fetch_neuron(root_id, client):
    df = client.materialize.query_table('nodes')
    return df[df['id'].isin([root_id])].to_dict(orient='records')
