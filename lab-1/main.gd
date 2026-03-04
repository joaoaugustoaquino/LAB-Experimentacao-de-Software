extends Node

const GITHUB_TOKEN = "your_classic_token"
const ENDPOINT = "https://api.github.com/graphql"
const TARGET_TOTAL = 1000

@onready var http: HTTPRequest = $HTTPRequest

var repo_list: Array = []

var current_index := 0
var total_collected := 0
var next_cursor: String = ""
var has_next_page := true

var phase := "search_page"

var file: FileAccess


func _ready():
	http.request_completed.connect(_on_request_completed)
	
	file = FileAccess.open("user://repos.csv", FileAccess.WRITE)
	file.store_line("name,created_at,updated_at,language,merged_prs,releases,total_issues,closed_issues,issue_ratio")
	
	fetch_repos_page()

func fetch_repos_page():
	
	var headers = _get_headers()
	
	var after_part = ""
	if next_cursor != "":
		after_part = ', after: "%s"' % next_cursor
	
	var query_dict = {
		"query": """
		query {
			search(
				query: "stars:>10000 sort:stars-desc",
				type: REPOSITORY,
				first: 100%s
			) {
				pageInfo {
					hasNextPage
					endCursor
				}
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
		""" % after_part
	}
	
	phase = "search_page"
	
	http.request(
		ENDPOINT,
		headers,
		HTTPClient.METHOD_POST,
		JSON.stringify(query_dict)
	)


func fetch_repo_details(owner: String, name: String):
	
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
		""" % [owner, name]
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
	
	
	if phase == "search_page":
		
		var search_data = json_data["data"]["search"]
		
		repo_list = search_data["nodes"]
		next_cursor = search_data["pageInfo"]["endCursor"]
		has_next_page = search_data["pageInfo"]["hasNextPage"]
		
		current_index = 0
		
		print("Página recebida. Total acumulado:", total_collected)
		
		_process_next_repo()
	
	
	elif phase == "details":
		
		var repo_basic = repo_list[current_index]
		var repo_metrics = json_data["data"]["repository"]
		
		var open_issues = repo_metrics["openIssues"]["totalCount"]
		var closed_issues = repo_metrics["closedIssues"]["totalCount"]
		var total_issues = open_issues + closed_issues
		
		var issue_ratio = 0.0
		if total_issues > 0:
			issue_ratio = float(closed_issues) / float(total_issues)
			
		file.store_line("%s,%s,%s,%s,%d,%d,%d,%d,%f" % [
			repo_basic["nameWithOwner"],
			repo_basic["createdAt"],
			repo_basic["updatedAt"],
			repo_basic["primaryLanguage"]["name"] if repo_basic["primaryLanguage"] != null else "N/A",
			repo_metrics["pullRequests"]["totalCount"],
			repo_metrics["releases"]["totalCount"],
			total_issues,
			closed_issues,
			issue_ratio
		])
		
		total_collected += 1
		current_index += 1
		
		if total_collected % 50 == 0:
			print("Coletados:", total_collected)
		
		if total_collected >= TARGET_TOTAL:
			_finish_collection()
			return
		
		_process_next_repo()


func _process_next_repo():
	
	if current_index >= repo_list.size():
		
		if has_next_page and total_collected < TARGET_TOTAL:
			fetch_repos_page()
		else:
			_finish_collection()
		return
	
	var repo = repo_list[current_index]
	var split = repo["nameWithOwner"].split("/")
	
	fetch_repo_details(split[0], split[1])

func _finish_collection():
	
	print("FINALIZADO. Total:", total_collected)
	
	file.close()
	
	print("CSV gerado em user://repos.csv")
