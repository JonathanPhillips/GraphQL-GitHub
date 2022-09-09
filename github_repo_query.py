from python_graphql_client import GraphqlClient
from pandas.io.json import json_normalize
import pandas as pd

client = GraphqlClient(endpoint="https://api.github.com/graphql")

def make_query(after_cursor=None):
    return """
{
  search(query: "org:<yourORGhere>", type: REPOSITORY, first: 100, after:AFTER) {
    repositoryCount
    pageInfo {
      startCursor
      hasNextPage
      endCursor
    }
edges {
      node {
        ... on Repository {
          name
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def fetch_repos(oauth_token):
    repos = []
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": "Bearer {}".format(oauth_token)},
        )
        normalized_data = data["data"]["search"]["edges"] #drill down into dictionary
        for repo in normalized_data:
            repos.append(repo)
            
        has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
    return repos

    
api_token = "XXXXXXXXXXXXXX" # replace with github token or env var
repos = fetch_repos(api_token)
normalized_repos = pd.json_normalize(repos) #flatten out the json with pandas
renamed_repos = normalized_repos[['node.name']] 
renamed_repos.columns = [['Repo Name']] #rename the column from node.name to Repo Name
output = "github_repo.csv"
renamed_repos.to_csv(output, index=False) #Save to CSV without index
