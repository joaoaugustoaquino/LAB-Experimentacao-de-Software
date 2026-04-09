extends Node

var data = []
@onready var languague_chart: Node = $LanguagueChart
@onready var pr_histogram: Node = $PRHistogram
@onready var issue_ratio_histogram: Node = $IssueRatioHistogram

func _ready():

	load_csv()
	languague_chart.set_data(data)
	pr_histogram.set_data(data)
	issue_ratio_histogram.set_data(data)

func load_csv():

	var file = FileAccess.open("user://repos.csv", FileAccess.READ)

	if file == null:
		print("Erro abrindo CSV")
		return

	file.get_line() # pula header

	while !file.eof_reached():

		var line = file.get_line()
		if line == "":
			continue

		var cols = line.split(",")

		var repo = {
			"language": cols[3],
			"prs": int(cols[4]),
			"releases": int(cols[5]),
			"issue_ratio": float(cols[8])
		}

		data.append(repo)

	file.close()

	print("Dados carregados:", data.size())
