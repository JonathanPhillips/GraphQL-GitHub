from python_graphql_client import GraphqlClient
from pandas.io.json import json_normalize
import pandas as pd

client = GraphqlClient(endpoint="https://api.github.com/graphql")

def make_query(after_cursor=None):
    return """
{
  search(query: "org:Caremetx", type: REPOSITORY, first: 100, after: AFTER) {
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
          collaborators {
            edges {
              node {
                login
              }
            }
          }
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )

def fetch_repos_users(oauth_token):
    repos = []
    repousers = []
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

            ''' repousers.append(
                {
                    "collaborator": repo[0]["edges"]
                }
            ) '''
            
        has_next_page = data["data"]["search"]["pageInfo"]["hasNextPage"]
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
    return repos

api_token = "XXXXXXXXXXXXXXXXXX" #replace with api key or env var
repos = fetch_repos_users(api_token)
normalized_repos = pd.json_normalize(repos) #flatten out the json with pandas

renamed_repos = normalized_repos[['node.name', 'node.collaborators.edges']]
exploded = renamed_repos.explode("node.collaborators.edges")
repos_with_users = pd.concat([exploded["node.name"].reset_index(drop=True), pd.json_normalize(exploded["node.collaborators.edges"])], axis=1) #normalize the nested json in second colum and concatenate back with original column

repos_with_users.columns = [['Repo Name', 'Collaborators']]  # rename columns
output = "github_repo_users.csv"
repos_with_users.to_csv(output, index=False) #Save to CSV without index
