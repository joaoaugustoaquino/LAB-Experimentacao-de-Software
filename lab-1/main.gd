extends Node

const GITHUB_TOKEN = "SECRET_KEY" # PERSONAL TOKEN CLASSIC
const ENDPOINT = "https://api.github.com/graphql"

@onready var http: HTTPRequest = $HTTPRequest

var repo_list: Array = []
var current_index := 0
var dataset: Array = []
var phase := "search"

func _ready():
	http.request_completed.connect(_on_request_completed)
	fetch_top_100()

# PRIMEIRA QUERY
func fetch_top_100():
	var headers = _get_headers()
	
	var query_dict = {
		"query": """
		query {
			search(
				query: "stars:>10000 sort:stars-desc",
				type: REPOSITORY,
				first: 100
			) {
				nodes {
					... on Repository {
						nameWithOwner
						createdAt
						updatedAt
						primaryLanguage { name }
					}
				}
			}
		}
		"""
	}
	
	phase = "search"
	
	http.request(
		ENDPOINT,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(query_dict)
	)

# SEGUNDA QUERY (POR REPO)
func fetch_repo_details(_owner: String, _name: String):
	var headers = _get_headers()
	
	var query_dict = {
		"query": """
		query {
			repository(owner: "%s", name: "%s") {
				pullRequests(states: MERGED) { totalCount }
				releases { totalCount }
				openIssues: issues(states: OPEN) { totalCount }
				closedIssues: issues(states: CLOSED) { totalCount }
			}
		}
		""" % [_owner, _name]
	}
	
	phase = "details"
	
	http.request(
		ENDPOINT,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(query_dict)
	)


func _get_headers():
	return [
		"Authorization: Bearer " + GITHUB_TOKEN,
		"Content-Type: application/json",
		"User-Agent: GodotEngine"
	]

# CALLBACK
func _on_request_completed(_result, response_code, _headers, body):
	var response_text = body.get_string_from_utf8()
	
	if response_code != 200:
		print("Erro HTTP:", response_code)
		print(response_text)
		return
	
	var json_data = JSON.parse_string(response_text)
	
	if json_data == null or json_data.has("errors"):
		print("Erro GraphQL:", response_text)
		return
	
	# FASE 1 - RECEBE LISTA
	if phase == "search":
		repo_list = json_data["data"]["search"]["nodes"]
		current_index = 0
		print("Repos encontrados:", repo_list.size())
		
		_process_next_repo()
	
	# FASE 2 - RECEBE MÉTRICAS
	elif phase == "details":
		var repo_basic = repo_list[current_index]
		var repo_metrics = json_data["data"]["repository"]
		
		var owner_name = repo_basic["nameWithOwner"]
		var created_at = repo_basic["createdAt"]
		var updated_at = repo_basic["updatedAt"]
		
		var language = "N/A"
		if repo_basic["primaryLanguage"] != null:
			language = repo_basic["primaryLanguage"]["name"]
		
		var merged_prs = repo_metrics["pullRequests"]["totalCount"]
		var releases = repo_metrics["releases"]["totalCount"]
		
		var open_issues = repo_metrics["openIssues"]["totalCount"]
		var closed_issues = repo_metrics["closedIssues"]["totalCount"]
		
		var total_issues = open_issues + closed_issues
		var issue_ratio = 0.0
		if total_issues > 0:
			issue_ratio = float(closed_issues) / float(total_issues)
		
		dataset.append({
			"name": owner_name,
			"created_at": created_at,
			"updated_at": updated_at,
			"language": language,
			"merged_prs": merged_prs,
			"releases": releases,
			"total_issues": total_issues,
			"closed_issues": closed_issues,
			"issue_ratio": issue_ratio
		})
		
		current_index += 1
		_process_next_repo()

# PROCESSA SEQUENCIALMENTE
func _process_next_repo():
	if current_index >= repo_list.size():
		print("FINALIZADO.")
		print("Total coletado:", dataset.size())
		return
	
	var repo = repo_list[current_index]
	var split = repo["nameWithOwner"].split("/")
	
	var _owner = split[0]
	var _name = split[1]
	
	print("Coletando:", _owner, "/", _name, "(", current_index+1, ")")
	
	fetch_repo_details(_owner, _name)
